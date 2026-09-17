from pathlib import Path
from io import BytesIO
import time
import zlib
import zipfile
import olefile
import pytest
from jto_cloud.contracts import template_info,validate_document,select_template,ROOT
from jto_cloud.state import State
from jto_cloud.service import Documents
from jto_cloud.hwpx import inspect_hwpx
from jto_cloud.hwp import records
from samples import sample


@pytest.fixture
def service(tmp_path):return Documents(tmp_path,State(tmp_path/'state.db'),'https://example.test','x'*40,3600)


def test_templates_and_routing():
    assert all(t['available'] for t in template_info())
    assert select_template('2027 중화권 마케팅 사업계획')=='business_plan'
    assert select_template('성과 결과보고')=='result_report'
    assert select_template('사업계획을 1PAGE 보고서로')=='onepage'


@pytest.mark.parametrize('kind',['business_plan','result_report','onepage'])
def test_generate_original_formats(service,kind):
    value=sample(kind)
    assert validate_document(kind,value)['valid']
    result=service.generate(kind,value,'alice')
    assert [f['name'] for f in result['files']]==['report.'+('hwp' if kind=='onepage' else 'hwpx')]
    ext='hwp' if kind=='onepage' else 'hwpx'
    folder=service.root/result['artifact_id'];p=folder/('report.'+ext)
    if ext=='hwpx':
        info=inspect_hwpx(p)
        text=' '.join(x for s in info['sections'] for x in s['paragraphs'])
        assert '중화권 마케팅' in text
        assert 'HY헤드라인M' not in text
        assert '표 작성 필요시' not in text
        assert ('향후계획' if kind=='result_report' else '기대효과') in text
        with zipfile.ZipFile(p) as out,zipfile.ZipFile(ROOT/('result-report.hwpx' if kind=='result_report' else 'business-plan.hwpx')) as original:
            assert out.read('Contents/header.xml')==original.read('Contents/header.xml')
            for name in original.namelist():
                if name.startswith('BinData/'):assert original.read(name)==out.read(name)
    else:
        with olefile.OleFileIO(p) as out,olefile.OleFileIO(ROOT/'onepage.hwp') as original:
            assert len(records(zlib.decompress(out.openstream('DocInfo').read(),-15)))==len(records(zlib.decompress(original.openstream('DocInfo').read(),-15)))+1
            assert out.openstream('FileHeader').read()==original.openstream('FileHeader').read()
            rs=records(zlib.decompress(out.openstream('BodyText/Section0').read(),-15))
            text=''.join(d.decode('utf-16le') for t,l,d in rs if t==67)
            assert value['title'] in text and '글상자 테두리선' not in text
            assert '편집여백' not in text
    assert not (folder/'sources.md').exists()
    assert '검사 범위*' in text and '확인 필요*' in text


def test_boundaries(service):
    v=sample('onepage');v['sections']*=2
    assert not validate_document('onepage',v)['valid']
    v=sample('business_plan');v['budget']['status']='confirmed';v['budget']['declared_total']=20
    assert not validate_document('business_plan',v)['valid']
    v=sample('result_report');v['budget']['status']='proposed'
    assert not validate_document('result_report',v)['valid']
    v=sample('business_plan');v['sections']['background'][0]['text']='사례 [S1]'
    assert not validate_document('business_plan',v)['valid']


def test_download_scope_tamper_expiry(service):
    r=service.generate('business_plan',sample('business_plan'),'alice')
    a=r['artifact_id'];exp=r['expires_at'];sig=service.signature(a,'report.hwpx',exp)
    assert service.resolve(a,'report.hwpx',exp,sig).is_file()
    assert service.resolve(a,'report.hwpx',exp,'wrong') is None
    assert service.resolve(a,'../state.db',exp,sig) is None
    assert service.resolve(a,'report.hwpx',0,sig) is None
    with pytest.raises(ValueError):service.links(a,'bob')
