"""Server-owned integrations. No caller-supplied commands, paths or fetch URLs."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import threading
from urllib.parse import quote
import httpx

_render_lock=threading.Lock()
AUTO_REV='d96d1f2f40458dc3d4470392524dcda9e43ac304'


def status():
    return {
        'auto_hwp': {'available':bool(shutil.which('auto-hwp')), 'revision':AUTO_REV,
                     'scope':'PDF rendering on server; not native Hancom verification'},
        'paper_verify':{'mode':'independent reference-check workflow; upstream code not redistributed',
                        'upstream':'https://github.com/chrisryugj/paper-verify',
                        'limitation':'upstream is a skill, not an MCP endpoint; no redistribution license found'},
        'hangul_spellchecker':{'mode':'Hunspell server adapter; upstream application not bundled',
                              'available':bool(shutil.which('hunspell')),
                              'upstream':'https://gitlab.aigov.go.kr/jhoh9505/hangul-spellchecker',
                              'limitation':'upstream own-code license unconfirmed; custom public-language rules not included'}}


def spellcheck(text):
    if not 1<=len(text)<=12000:raise ValueError('검사 본문은 1~12000자')
    binary=shutil.which('hunspell')
    if not binary:return {'checked':False,'reason':'서버 Hunspell 엔진 미설치','issues':[]}
    # ^ forces each line to be treated as input, never an interactive command.
    result=subprocess.run([binary,'-d','ko_KR','-i','UTF-8','-a'],input='\n'.join('^'+line for line in text.splitlines())+'\n',
                          encoding='utf-8',capture_output=True,timeout=15,check=False)
    if result.returncode:return {'checked':False,'reason':'사전 또는 엔진 실행 실패','issues':[]}
    issues=[]
    for line in result.stdout.splitlines():
        if line.startswith(('& ','# ')):
            parts=line.split(':',1);word=parts[0].split()[1]
            if any(x['word']==word for x in issues):continue
            issues.append({'word':word,'suggestions':parts[1].strip().split(', ')[:5] if len(parts)>1 else []})
            if len(issues)>=80:break
    return {'checked':True,'engine':'Hunspell ko_KR','issues':issues,
            'scope':'사전 기반 의심 표기이며 고유명사·음슴체 오탐 가능함. 자동 수정 및 문장호응·사실 검증 아님'}


def verify_doi(doi, expected_title=''):
    doi=re.sub(r'^https?://(?:dx\.)?doi\.org/','',doi.strip(),flags=re.I)
    if len(doi)>200 or not re.fullmatch(r'10\.\d{4,9}/[^\s]+',doi):raise ValueError('올바른 DOI 입력 필요')
    try:
        with httpx.Client(timeout=15,follow_redirects=False) as client:
            response=client.get('https://api.crossref.org/works/'+quote(doi,safe=''),headers={'User-Agent':'JTO-Cloud-MCP/0.2 (reference verification)'})
        if response.status_code!=200:return {'status':'미검증','doi':doi,'reason':'Crossref 단일 조회로 확인되지 않음. 허위 인용으로 단정 불가','content_verified':False}
        data=response.json()['message'];title=(data.get('title') or [''])[0]
        norm=lambda s:re.sub(r'\W','',s).casefold()
        return {'status':'서지 조회 완료' if not expected_title or norm(expected_title)==norm(title) else '제목 불일치 확인 필요',
                'doi':doi,'title':title,'publisher':data.get('publisher'),
                'source':'https://api.crossref.org/works/'+quote(doi,safe=''),
                'content_verified':False,'note':'DOI 실존·서지 조회임. 주장·인용 쪽수는 원문 전문 대조 필요함'}
    except (httpx.HTTPError,ValueError,KeyError):return {'status':'미검증','doi':doi,'content_verified':False,'reason':'조회 실패 또는 응답 형식 오류'}


def render_pdf(document):
    binary=shutil.which('auto-hwp')
    if not binary:return {'rendered':False,'reason':'auto-hwp 미설치','visual_verified':False}
    if not _render_lock.acquire(blocking=False):return {'rendered':False,'reason':'렌더링 작업 처리 중','visual_verified':False}
    target=Path(document).with_suffix('.pdf')
    try:
        result=subprocess.run([binary,'export-pdf',str(Path(document).resolve()),'-o',str(target.resolve())],
                              stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=45)
        if result.returncode or not target.is_file():raise ValueError('render failed')
        from pypdf import PdfReader
        count=len(PdfReader(target).pages)
        if not count:raise ValueError('empty pdf')
        return {'rendered':True,'engine':'auto-hwp','pages':count,'visual_verified':False,
                'note':'독립 엔진·대체 글꼴 PDF임. 한글 원본 조판 검증 아님'}
    except (OSError,ValueError,subprocess.TimeoutExpired):
        target.unlink(missing_ok=True)
        return {'rendered':False,'reason':'auto-hwp 변환 실패 또는 시간 초과','visual_verified':False}
    finally:_render_lock.release()
