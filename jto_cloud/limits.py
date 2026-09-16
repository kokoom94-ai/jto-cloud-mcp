from starlette.responses import PlainTextResponse


class RequestLimits:
    def __init__(self, app, state):self.app,self.state=app,state

    async def __call__(self, scope, receive, send):
        if scope['type']!='http':return await self.app(scope,receive,send)
        ip=(scope.get('client') or ('unknown',0))[0]
        path=scope.get('path','')
        if path=='/register' and not self.state.allow('register:'+ip,20,3600):
            return await PlainTextResponse('Registration limit reached',429)(scope,receive,send)
        # Buffer only bounded bodies, including the OAuth form endpoints.
        if scope['method'] in ('POST','PUT','PATCH'):
            chunks=[];size=0
            while True:
                message=await receive()
                if message['type']=='http.disconnect':return
                if message['type']!='http.request':continue
                chunk=message.get('body',b'');size+=len(chunk)
                if size>1024*1024:return await PlainTextResponse('Request too large',413)(scope,receive,send)
                chunks.append(chunk)
                if not message.get('more_body',False):break
            delivered=False
            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered=True
                    return {'type':'http.request','body':b''.join(chunks),'more_body':False}
                return await receive()
            return await self.app(scope,bounded_receive,send)
        return await self.app(scope,receive,send)
