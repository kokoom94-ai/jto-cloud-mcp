import struct
import zlib
from zipfile import ZipFile
from xml.dom import minidom
import olefile
import pytest
from samples import sample
from jto_cloud.contracts import validate_document,ROOT
from jto_cloud.hwpx import render_hwpx,paragraph_text
from jto_cloud.hwp import generate_onepage,records
from jto_cloud.integrations import verify_doi,spellcheck


def evidence(kind):
    v=sample(kind)
    v['research']['sources']=[{'id':'S1','title':'관광 통계','url':'https://example.org/report',
        'published':'2026-09-01','checked_on':'2026-09-17','country':'한국','insight':'지표 정의 참고함'}]
    v['annotations']=[{'anchor':'체류','note':'숙박을 포함한 방문 기간임','source_ids':['S1'],'verification':'원문 수치 대조 미완료'}]
    if kind=='onepage':
        v['sections']=[{'heading':'추진방향','bullets':['체류 확대 추진 예정 [S1]']}]
    else:v['sections'][next(iter(v['sections']))]=[{'text':'체류 확대 추진 예정 [S1]'}]
    return v


@pytest.mark.parametrize('kind',['business_plan','result_report'])
def test_inline_evidence_original_note_style(tmp_path,kind):
    v=evidence(kind);target=tmp_path/'report.hwpx'
    render_hwpx(ROOT/('business-plan.hwpx' if kind=='business_plan' else 'result-report.hwpx'),target,v,kind)
    with ZipFile(target) as z:
        doc=minidom.parseString(z.read('Contents/section0.xml'));header=minidom.parseString(z.read('Contents/header.xml'))
    ps=doc.getElementsByTagName('hp:p');texts=[paragraph_text(p) for p in ps]
    assert any('체류* 확대 추진 예정 *S1' in t for t in texts)
    notes=[p for p in ps if '출처: 관광 통계' in paragraph_text(p) or '체류: 숙박' in paragraph_text(p)]
    assert len(notes)==2
    for p in notes:
        ref=p.getElementsByTagName('hp:run')[0].getAttribute('charPrIDRef')
        shape=next(x for x in header.getElementsByTagName('hh:charPr') if x.getAttribute('id')==ref)
        assert shape.getAttribute('height')=='1200'
        font=shape.getElementsByTagName('hh:fontRef')[0].getAttribute('hangul')
        fonts=next(f for f in header.getElementsByTagName('hh:fontface') if f.getAttribute('lang')=='HANGUL')
        face=next(f for f in fonts.getElementsByTagName('hh:font') if f.getAttribute('id')==font)
        assert '중고딕' in face.getAttribute('face')
    assert any('원문 수치 대조 미완료' in t for t in texts)


def test_hwp_note_shape_and_evidence(tmp_path):
    target=tmp_path/'report.hwp';v=evidence('onepage')
    assert validate_document('onepage',v)['valid']
    generate_onepage(ROOT/'onepage.hwp',target,v)
    with olefile.OleFileIO(target) as o:
        shapes=[d for t,l,d in records(zlib.decompress(o.openstream('DocInfo').read(),-15)) if t==21]
        body=records(zlib.decompress(o.openstream('BodyText/Section0').read(),-15))
    assert struct.unpack_from('<i',shapes[-1],42)[0]==1200
    assert struct.unpack_from('<H',shapes[-1],0)[0]==5
    text=' '.join(d.decode('utf-16le') for t,l,d in body if t==67)
    assert '체류*' in text and 'https://example.org/report' in text and '원문 수치 대조 미완료' in text


def test_editorial_rejection():
    v=sample('business_plan');v['sections']['background'][0]['text']='사업 추진을 제안합니다.'
    assert not validate_document('business_plan',v)['valid']
    v=evidence('onepage');v['annotations'][0]['anchor']='없는단어'
    assert not validate_document('onepage',v)['valid']
    v=evidence('onepage');v['annotations'][0]['source_ids']=['S99']
    assert not validate_document('onepage',v)['valid']
    v=evidence('onepage');v['annotations'][0]['note']='긴 설명'*150;v['annotations'][0]['verification']='검증 설명'*100
    assert not validate_document('onepage',v)['valid']


def test_integration_boundaries(monkeypatch):
    with pytest.raises(ValueError):verify_doi('http://127.0.0.1/private')
    with pytest.raises(ValueError):spellcheck('a'*12001)
    monkeypatch.setattr('jto_cloud.integrations.shutil.which',lambda _:None)
    assert spellcheck('검사함')['checked'] is False
