from copy import deepcopy
from hashlib import sha256
from pathlib import Path
from datetime import date
import json
import math
from .model import PLAN_SCHEMA, BLOCK, SECTION_TABLE, obj, array, string, validate_schema, MAX_MONEY

ROOT = Path(__file__).parent/'templates'
FILES = {'business_plan':'business-plan.hwpx','result_report':'result-report.hwpx','onepage':'onepage.hwp'}
RESULT_SECTIONS = {'overview':'추진개요','execution':'세부 추진내용','outcomes':'주요성과','issues':'문제점 및 개선방안','followup':'세부 추진계획(안)'}
TEMPLATE_HASHES = json.loads((ROOT/'hashes.json').read_text('utf-8'))
SCHEMAS = {'business_plan':deepcopy(PLAN_SCHEMA), 'result_report':deepcopy(PLAN_SCHEMA)}
SCHEMAS['result_report']['properties']['sections'] = obj({k:array(BLOCK) for k in RESULT_SECTIONS})
SCHEMAS['result_report']['properties']['section_tables'] = obj({k:SECTION_TABLE for k in ('outcomes','issues','followup')}, [])
SCHEMAS['result_report']['properties']['expected_effects']['description'] = '원본 결과보고 양식의 향후계획에 들어갈 내용'
for kind in SCHEMAS:
    s=SCHEMAS[kind]
    s['properties']['budget']['properties']['status']={'type':'string','enum':['proposed','confirmed','unknown']}
    s['properties']['budget']['required'].append('status')
    s['properties']['research']['description']='웹 조사 여부·기준일·실제 확인한 출처. 없으면 조사 미완료와 빈 sources.'
    s['required'] += ['research','missing_inputs']
    s['title']='JTO '+kind
SCHEMAS['onepage'] = obj({
    'title':string(22), 'subtitle':string(28), 'metadata':string(40),
    'summary':{'type':'array','items':string(28),'minItems':2,'maxItems':2},
    'sections':{'type':'array','items':obj({'heading':string(20),'bullets':array(string(52),3)}),'minItems':1,'maxItems':3},
    'note':string(48),
    'research':deepcopy(PLAN_SCHEMA['properties']['research']),
    'missing_inputs':deepcopy(PLAN_SCHEMA['properties']['missing_inputs']),
})

# Evidence is embedded in the original form, never a separate employee deliverable.
ANNOTATION = obj({'anchor':string(80),'note':string(600),
                  'source_ids':array(string(30),10),'verification':string(600)}, ['anchor','note'])
for schema in SCHEMAS.values():
    schema['properties']['annotations']={'type':'array','items':ANNOTATION,'maxItems':30}
    schema['properties']['annotations']['description']='본문 해당 단어 뒤 * 표시 및 중고딕 12pt 주석. 출처 ID와 실제 수행한 검증·미검증 사항 포함.'


def validate_document(kind, value):
    from jsonschema import Draft202012Validator, FormatChecker
    if kind not in SCHEMAS:
        return {'valid':False,'errors':['지원하지 않는 양식'],'warnings':[]}
    errors=[f"{'.'.join(map(str,e.absolute_path))}: {e.message}" for e in Draft202012Validator(SCHEMAS[kind],format_checker=FormatChecker()).iter_errors(value)]
    # Bound all XML/HWP strings and reject control characters even in optional data.
    def strings(v):
        if isinstance(v,str): yield v
        elif isinstance(v,dict):
            for a in v.values(): yield from strings(a)
        elif isinstance(v,list):
            for a in v: yield from strings(a)
    for text in strings(value):
        if any(ord(c)<32 or 0xd800<=ord(c)<=0xdfff or ord(c) in (0xfffe,0xffff) for c in text):
            errors.append('줄바꿈·제어문자는 개별 입력 필드에 사용할 수 없습니다.')
    total=0
    if not errors and kind!='onepage':
        budget=value['budget'];total=sum(x['amount'] for x in budget['items'])
        if total>MAX_MONEY:errors.append('예산 합계 한도 초과')
        if budget.get('declared_total',total)!=total:errors.append('예산 합계 불일치')
        if budget['status']=='unknown' and total!=0:errors.append('미확인 예산에는 금액을 입력할 수 없습니다.')
        if budget['status']=='unknown' and any('[미확인]' not in x['description'] for x in budget['items']):
            errors.append('미확인 예산 내역은 [미확인] 표시가 필요합니다.')
        if kind=='result_report' and budget['status']=='proposed':errors.append('결과보고의 실제 집행액을 추정액으로 대체할 수 없습니다.')
    if not errors and kind=='onepage':
        lines=sum(1+sum(math.ceil(len(b)/28) for b in s['bullets']) for s in value['sections'])
        if lines>15:errors.append('1PAGE 본문이 깁니다. 제목 포함 예상 15줄 이내로 요약해 주세요.')
    if not errors:
        from urllib.parse import urlparse
        for source in value['research']['sources']:
            u=urlparse(source['url'])
            if u.scheme not in ('http','https') or not u.hostname or u.username or u.password:
                errors.append('출처는 인증정보 없는 HTTP(S) 주소여야 합니다.')
        known={s['id'] for s in value['research']['sources']}
        import re
        for text in strings(value.get('sections',{})):
            for ref in re.findall(r'\[(S\d+)\]',text):
                if ref not in known:errors.append(f'출처 {ref}가 sources에 없습니다.')
    if not errors:
        from .editorial import style_errors,body_strings,end_notes,local_notes
        errors.extend(style_errors(kind,value))
        body=' '.join(body_strings(kind,value))
        ids=[s['id'] for s in value['research']['sources']]
        if len(ids)!=len(set(ids)):errors.append('중복 출처 ID 사용 불가')
        for a in value.get('annotations',[]):
            if a['anchor'] not in body:errors.append('주석 대상 단어가 본문에 없음: '+a['anchor'])
            if any(i not in ids for i in a.get('source_ids',[])):errors.append('주석의 출처 ID가 sources에 없음')
        if kind=='onepage':
            notes=end_notes(kind,value)+local_notes(body,value)
            lines=sum(1+sum(math.ceil(len(b)/28) for b in x['bullets']) for x in value['sections'])
            note_lines=sum(max(1,math.ceil(len(n)/52)) for n in notes)+math.ceil(len(value['note'])/52)
            if lines+note_lines>28:errors.append('1PAGE 본문과 12pt 주석의 합계 분량 초과. 근거를 삭제하지 말고 본문을 요약하거나 상세 보고서로 작성 필요')
    return {'valid':not errors,'errors':errors,'warnings':['내용·형식 검사는 사실 검증이나 한글 화면 검증을 대체하지 않습니다.'], 'budget_total':total,'facts_verified':False}


def template_info():
    return [{'id':k,'filename':v,'sha256':TEMPLATE_HASHES[k],
             'available':(ROOT/v).is_file() and sha256((ROOT/v).read_bytes()).hexdigest()==TEMPLATE_HASHES[k],
             'output_format':'hwp' if k=='onepage' else 'hwpx'} for k,v in FILES.items()]


def select_template(request):
    import re
    if re.search(r'1\s*(page|p|페이지)|한\s*장|1쪽|원페이지',request,re.I):return 'onepage'
    if re.search(r'결과\s*보고|실적\s*보고|성과\s*보고',request):return 'result_report'
    return 'business_plan'
