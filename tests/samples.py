from copy import deepcopy
from jto_cloud.model import SECTIONS
from jto_cloud.contracts import RESULT_SECTIONS

RESEARCH={'as_of':'2026-09-16','status':'조사 미완료','sources':[]}


def sample(kind):
    if kind=='onepage':return {
        'title':'2027 중화권 마케팅 추진안','subtitle':'검토용 · 실제 확정 사업 아님',
        'metadata':"('26. 9. 16, 담당부서 [미입력])",
        'summary':['(안) 개별여행객의 제주 체류 확대','예약 가능한 로컬 체험과 판매 채널 연계'],
        'sections':[
            {'heading':'추진방향','bullets':['(안) 중화권 시장별 수요 조사 후 타깃 선정','(안) 체류형 코스와 현지 판매 채널 연계']},
            {'heading':'실행계획','bullets':['(안) 분기별 공동 프로모션과 콘텐츠 운영','(안) 예약·이용 완료·직접 거래액 측정']},
            {'heading':'검토사항','bullets':['예산·담당부서·협력사는 [미확인]','2026년 실적은 [사용자 입력 대기]']}],
        'note':'검토용 예시. 조사·예산 확정 후 시행 여부 결정.',
        'research':deepcopy(RESEARCH),'missing_inputs':['예산','전년도 실적']}
    labels=RESULT_SECTIONS if kind=='result_report' else SECTIONS
    return {'project_name':'2027 중화권 마케팅','plan_title':'중화권 마케팅 '+('결과보고' if kind=='result_report' else '사업계획(안)'),
        'document_date':'2026-09-16','department':'[미입력]','author':'[미입력]','position':'[미입력]',
        'sections':{k:[{'text':'[미확인] 자료 입력 대기' if kind=='result_report' else '(안) '+v+' 검토',
                       'details':['서식·생성 기능 검증용 예시이며 실제 사업 실적 아님']}] for k,v in labels.items()},
        'budget':{'status':'unknown','account':'[미입력]','payment_method':'[미입력]',
                  'items':[{'category':'[미확인]','description':'[미확인] 예산 또는 집행내역 입력 대기','amount':0}]},
        'expected_effects':['(안) 내부 자료 확인 후 계획 보완 예정'],
        'research':deepcopy(RESEARCH),'missing_inputs':['확정 예산','실적 증빙'],'is_example':True}
