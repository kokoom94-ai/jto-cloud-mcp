import base64
import hashlib
import re
from urllib.parse import urlparse,parse_qs
import pytest
from starlette.testclient import TestClient
from jto_cloud.server import create_app
from samples import sample

PASSWORD='test-connection-password-12345'


def connect(client):
    registration=client.post('/register',json={'client_name':'Integration Test','redirect_uris':['https://client.example/callback'],'grant_types':['authorization_code','refresh_token'],'response_types':['code'],'token_endpoint_auth_method':'none'})
    assert registration.status_code==201,registration.text
    cid=registration.json()['client_id']
    verifier='a'*64
    challenge=base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip('=')
    authorize=client.get('/authorize',params={'client_id':cid,'redirect_uri':'https://client.example/callback','response_type':'code','code_challenge':challenge,'code_challenge_method':'S256','scope':'documents','state':'test-state','resource':'https://server.example/mcp'},follow_redirects=False)
    assert authorize.status_code in (302,303),authorize.text
    consent_url=authorize.headers['location']
    page=client.get(consent_url)
    assert page.status_code==200,page.text
    csrf=re.search('name="csrf" value="([^"]+)"',page.text).group(1)
    granted=client.post(consent_url,data={'csrf':csrf,'password':PASSWORD},follow_redirects=False,headers={'Origin':'https://server.example'})
    assert granted.status_code==303,granted.text
    query=parse_qs(urlparse(granted.headers['location']).query)
    assert query['state']==['test-state']
    data={'grant_type':'authorization_code','code':query['code'][0],'client_id':cid,'redirect_uri':'https://client.example/callback','code_verifier':verifier,'resource':'https://server.example/mcp'}
    token=client.post('/token',data=data)
    assert token.status_code==200,token.text
    assert client.post('/token',data=data).status_code==400
    return token.json(),cid


def rpc(client,token,method,params=None):
    response=client.post('/mcp',json={'jsonrpc':'2.0','id':1,'method':method,'params':params or {}},headers={
        'Authorization':'Bearer '+token,'Accept':'application/json, text/event-stream','MCP-Protocol-Version':'2025-11-25'})
    assert response.status_code==200,response.text
    return response.json()


def test_oauth_mcp_generation_download_and_refresh(tmp_path):
    app=create_app(tmp_path,'https://server.example',PASSWORD,'s'*40)
    with TestClient(app,base_url='https://server.example') as client:
        assert client.get('/health').json()['templates']==3
        assert client.get('/.well-known/oauth-authorization-server').status_code==200
        assert client.get('/.well-known/oauth-protected-resource/mcp').status_code==200
        assert client.post('/mcp',json={}).status_code==401
        assert client.post('/register',content=b'x'*(1024*1024+1)).status_code==413
        token,cid=connect(client)
        bearer=token['access_token']
        initialized=rpc(client,bearer,'initialize',{'protocolVersion':'2025-11-25','capabilities':{},'clientInfo':{'name':'test','version':'1'}})
        assert initialized['result']['serverInfo']['name']=='JTO Cloud Documents'
        tools=rpc(client,bearer,'tools/list')['result']['tools']
        assert 'jto_generate_document' in [t['name'] for t in tools]
        for kind in ('business_plan','result_report','onepage'):
            result=rpc(client,bearer,'tools/call',{'name':'jto_generate_document','arguments':{'template':kind,'content':sample(kind)}})['result']
            assert not result.get('isError'),result
            data=result['structuredContent']
            link=data['files'][0]['url']
            downloaded=client.get(link)
            assert downloaded.status_code==200
            assert downloaded.headers['content-disposition'].startswith('attachment;')
            assert downloaded.content[:2]==(b'\xd0\xcf' if kind=='onepage' else b'PK')
            assert client.get(link.replace('signature=','signature=x')).status_code==404
        old_refresh=token['refresh_token']
        refresh=client.post('/token',data={'grant_type':'refresh_token','refresh_token':old_refresh,'client_id':cid,'resource':'https://server.example/mcp'})
        assert refresh.status_code==200,refresh.text
        assert refresh.json()['refresh_token']!=old_refresh
        assert client.post('/token',data={'grant_type':'refresh_token','refresh_token':old_refresh,'client_id':cid}).status_code==400


def test_fail_closed_configuration(tmp_path):
    with pytest.raises(ValueError):create_app(tmp_path,'http://public.example',PASSWORD,'s'*40)
    with pytest.raises(ValueError):create_app(tmp_path,'https://public.example','short','s'*40)
