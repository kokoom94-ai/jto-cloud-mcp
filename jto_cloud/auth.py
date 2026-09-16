"""OAuth 2.1/PKCE with explicit deployment-owner consent; SDK handles protocol checks."""
import hashlib
import hmac
import html
import secrets
import time
from urllib.parse import urlparse
from starlette.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from mcp.server.auth.provider import AuthorizationCode, AuthorizationParams, AccessToken, RefreshToken, TokenError, AuthorizeError, RegistrationError, construct_redirect_uri
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken


def key(token):return hashlib.sha256(token.encode()).hexdigest()


class Provider:
    def __init__(self, state, origin, password):
        self.state,self.origin,self.password=state,origin,password

    async def get_client(self, client_id):
        item=self.state.get('client',client_id)
        return OAuthClientInformationFull.model_validate(item) if item else None

    async def register_client(self, client_info):
        for uri in client_info.redirect_uris:
            url=urlparse(str(uri))
            if url.scheme!='https' and not (url.scheme=='http' and url.hostname in ('localhost','127.0.0.1','::1')):
                raise RegistrationError('invalid_redirect_uri','HTTPS redirect URI required')
        self.state.put('client',client_info.client_id,client_info.model_dump(mode='json'),365*86400)

    async def authorize(self, client, params):
        if params.resource and params.resource.rstrip('/')!=self.origin+'/mcp':
            raise AuthorizeError('invalid_request','Wrong resource')
        ticket=secrets.token_urlsafe(32)
        self.state.put('pending',key(ticket),{'client_id':client.client_id,'params':params.model_dump(mode='json')},600)
        return self.origin+'/consent?ticket='+ticket

    async def consent(self, request):
        headers={'Cache-Control':'no-store','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY',
                 'Content-Security-Policy':"default-src 'none'; form-action 'self'; style-src 'unsafe-inline'; frame-ancestors 'none'"}
        ticket=request.query_params.get('ticket','')
        pending=self.state.get('pending',key(ticket))
        if not pending:return PlainTextResponse('연결 요청이 만료됐습니다. AI에서 다시 연결하세요.',400,headers=headers)
        client=await self.get_client(pending['client_id'])
        if not client:return PlainTextResponse('Unknown client',400,headers=headers)
        if request.method=='POST':
            if request.headers.get('origin') not in (None,self.origin):return PlainTextResponse('Origin rejected',403)
            data=await request.form()
            if not hmac.compare_digest(str(data.get('csrf','')),request.cookies.get('jto_csrf','')) or not request.cookies.get('jto_csrf'):
                return PlainTextResponse('Invalid consent',403,headers=headers)
            if not self.state.allow('login:'+str(request.client.host),10,600):return PlainTextResponse('잠시 후 다시 시도하세요.',429,headers=headers)
            if not hmac.compare_digest(hashlib.sha256(str(data.get('password','')).encode()).digest(),hashlib.sha256(self.password.encode()).digest()):
                return PlainTextResponse('연결 암호가 올바르지 않습니다. 뒤로 가서 다시 입력하세요.',403,headers=headers)
            pending=self.state.get('pending',key(ticket),consume=True)
            if not pending:return PlainTextResponse('Already used',400,headers=headers)
            params=AuthorizationParams.model_validate(pending['params'])
            code=AuthorizationCode(code=secrets.token_urlsafe(32),client_id=client.client_id,scopes=params.scopes or ['documents'],
                expires_at=time.time()+120,code_challenge=params.code_challenge,redirect_uri=params.redirect_uri,
                redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,resource=self.origin+'/mcp',subject=secrets.token_hex(24))
            self.state.put('code',key(code.code),code.model_dump(mode='json'),120)
            return RedirectResponse(construct_redirect_uri(str(params.redirect_uri),code=code.code,state=params.state),303,headers=headers)
        csrf=secrets.token_urlsafe(32)
        text=f'''<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>JTO 문서 연결</title>
        <style>body{{max-width:520px;margin:70px auto;padding:24px;font-family:sans-serif;line-height:1.7}}input,button{{padding:14px;font-size:16px;width:100%;box-sizing:border-box;margin:10px 0}}button{{background:#115e59;color:white;border:0}}</style>
        <h1>JTO 문서 도구 연결</h1><p><strong>{html.escape(client.client_name or 'AI 앱')}</strong>에 양식 조회와 문서 생성 권한을 부여합니다.</p>
        <p>연결 대상: {html.escape(urlparse(pending['params']['redirect_uri']).hostname or '')}</p>
        <p>운영자가 전달한 연결 암호를 입력하세요. 암호는 AI 대화창에 입력하지 마세요.</p>
        <form method="post"><input type="hidden" name="csrf" value="{csrf}"><label>연결 암호<input name="password" type="password" required autocomplete="current-password"></label><button>동의하고 연결</button></form></html>'''
        response=HTMLResponse(text,headers=headers)
        response.set_cookie('jto_csrf',csrf,httponly=True,secure=self.origin.startswith('https:'),samesite='lax',max_age=600,path='/consent')
        return response

    async def load_authorization_code(self, client, authorization_code):
        raw=self.state.get('code',key(authorization_code))
        return AuthorizationCode.model_validate(raw) if raw and raw['client_id']==client.client_id else None

    def issue(self, client_id, scopes, subject):
        access=AccessToken(token=secrets.token_urlsafe(40),client_id=client_id,scopes=scopes,expires_at=int(time.time())+3600,resource=self.origin+'/mcp',subject=subject)
        refresh=RefreshToken(token=secrets.token_urlsafe(40),client_id=client_id,scopes=scopes,expires_at=int(time.time())+30*86400,resource=self.origin+'/mcp',subject=subject)
        self.state.put('access',key(access.token),access.model_dump(mode='json'),3600)
        self.state.put('refresh',key(refresh.token),refresh.model_dump(mode='json'),30*86400)
        self.state.put('pair',key(access.token),key(refresh.token),30*86400)
        self.state.put('pair',key(refresh.token),key(access.token),30*86400)
        return OAuthToken(access_token=access.token,refresh_token=refresh.token,token_type='Bearer',expires_in=3600,scope=' '.join(scopes))

    async def exchange_authorization_code(self, client, authorization_code):
        raw=self.state.get('code',key(authorization_code.code),consume=True)
        if not raw or raw['client_id']!=client.client_id:raise TokenError('invalid_grant','Code expired or used')
        return self.issue(client.client_id,authorization_code.scopes,authorization_code.subject)

    async def load_refresh_token(self, client, refresh_token):
        raw=self.state.get('refresh',key(refresh_token))
        return RefreshToken.model_validate(raw) if raw and raw['client_id']==client.client_id else None

    async def exchange_refresh_token(self, client, refresh_token, scopes):
        raw=self.state.get('refresh',key(refresh_token.token),consume=True)
        if not raw or raw['client_id']!=client.client_id or not set(scopes)<=set(raw['scopes']):raise TokenError('invalid_grant','Invalid refresh token')
        await self.revoke_token(refresh_token)
        return self.issue(client.client_id,scopes,refresh_token.subject)

    async def load_access_token(self, token):
        raw=self.state.get('access',key(token))
        return AccessToken.model_validate(raw) if raw else None

    async def revoke_token(self, token):
        first=key(token.token);second=self.state.get('pair',first)
        for k in (first,second):
            if k:
                for kind in ('access','refresh','pair'):self.state.delete(kind,k)
