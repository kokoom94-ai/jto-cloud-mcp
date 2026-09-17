"""Internal approval/report voice and in-document evidence notes."""
import re

STYLE = '상사 보고·내부 품의용 음슴체 사용. ~함/~임/~예정/~필요 등으로 종결. 제안한다/추천합니다/해보세요 등 AI 조언 어투 금지. 미확정 계획은 (안), 추정액은 산정 가정으로 구분.'
REF = re.compile(r'\[(S\d+)\]')


def body_strings(kind, content):
    if kind == 'onepage':
        yield from content['summary']
        for section in content['sections']:
            yield from section['bullets']
        yield content['note']
    else:
        for blocks in content['sections'].values():
            for block in blocks:
                yield block['text']
                yield from block.get('details', [])
                yield from block.get('subdetails', [])
                if block.get('note'): yield block['note']
        yield from content['expected_effects']


def style_errors(kind, content):
    errors=[]
    for text in body_strings(kind, content):
        if re.search(r'제안(?:한다|합니다|함)|추천(?:한다|합니다|함)|해\s*보세요|하시기\s*바랍니다|[가-힣](?:습니다|합니다|해요|하세요)(?:[.!?]|$)|[가-힣](?:한다|된다|이다)(?:[.!?]|$)',text):
            errors.append('보고·품의용 음슴체로 수정 필요: '+text[:80])
        if '[제안]' in text: errors.append('[제안] 대신 계획(안)·추진 예정 등 내부 품의 표현 사용 필요')
    return errors


def mark(text, content):
    text=REF.sub(lambda m:'*'+m[1],text)
    for a in content.get('annotations',[]):
        anchor=a['anchor']
        text=re.sub(re.escape(anchor)+r'(?!\*)',lambda m:m[0]+'*',text)
    return text


def source_note(source):
    return f"{source['id']} 출처: {source['title']} ({source['published']}); {source['url']}; 확인일 {source['checked_on']}; 근거: {source['insight']}"


def local_notes(text, content):
    notes=[]
    ids=set(REF.findall(text))
    for a in content.get('annotations',[]):
        if a['anchor'] in text:
            notes.append(a['anchor']+': '+a['note'])
            ids.update(a.get('source_ids',[]))
            if a.get('verification'):notes.append(a['anchor']+' 검증: '+a['verification'])
    for s in content['research']['sources']:
        if s['id'] in ids: notes.append(source_note(s))
    return notes


def end_notes(kind, content):
    texts=list(body_strings(kind,content))
    notes=[]
    referenced=set(REF.findall(' '.join(texts)))
    for a in content.get('annotations',[]):referenced.update(a.get('source_ids',[]))
    for s in content['research']['sources']:
        if s['id'] not in referenced:notes.append(source_note(s))
    notes.append('조사·검증 기준*: '+content['research']['as_of']+' / '+content['research']['status'])
    if content['missing_inputs']:notes.append('확인 필요*: '+'; '.join(content['missing_inputs']))
    notes.append('검사 범위*: 입력 구조·예산 합계 검사 수행함. 사실관계·원문 대조·한글 조판 검증 완료를 의미하지 않음')
    return notes
