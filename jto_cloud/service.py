from pathlib import Path
from hashlib import sha256
import hmac
import html
import json
import secrets
import time
import zipfile
from .contracts import FILES,ROOT,TEMPLATE_HASHES,validate_document
from .hwpx import render_hwpx,validate_hwpx
from .hwp import generate_onepage


class Documents:
    def __init__(self, data_dir, state, base_url, signing_key, ttl=86400):
        self.root=Path(data_dir)/'artifacts';self.root.mkdir(parents=True,exist_ok=True)
        self.state,self.base,self.secret,self.ttl=state,base_url,signing_key.encode(),ttl

    def signature(self, artifact, filename, expiry):
        return hmac.new(self.secret,f'{artifact}/{filename}/{expiry}'.encode(),sha256).hexdigest()

    def links(self, artifact, owner):
        info=self.state.get('artifact',artifact)
        if not info or info['owner']!=owner:raise ValueError('문서를 찾을 수 없거나 만료되었습니다.')
        exp=info['expiry']
        return {'artifact_id':artifact,'expires_at':exp,'files':[{
            'name':n,'url':f'{self.base}/download/{artifact}/{n}?expires={exp}&signature={self.signature(artifact,n,exp)}',
            'size':(self.root/artifact/n).stat().st_size} for n in info['files']], 'validation':info['validation']}

    def resolve(self, artifact, filename, expiry, signature):
        # Whitelisted manifest membership before filesystem use. No arbitrary path input.
        info=self.state.get('artifact',artifact)
        if not info or filename not in info['files'] or expiry!=info['expiry'] or expiry<int(time.time()):return None
        if not hmac.compare_digest(signature,self.signature(artifact,filename,expiry)):return None
        return self.root/artifact/filename

    def cleanup(self):
        import shutil
        now=time.time()
        for folder in self.root.iterdir():
            if folder.is_dir() and folder.stat().st_mtime+self.ttl+300<now:
                shutil.rmtree(folder)
        self.state.purge()

    def generate(self, kind, content, owner):
        check=validate_document(kind,content)
        if not check['valid']:raise ValueError('; '.join(check['errors']))
        if sha256((ROOT/FILES[kind]).read_bytes()).hexdigest()!=TEMPLATE_HASHES[kind]:raise ValueError('원본 양식 해시 불일치')
        self.cleanup()
        # Keep this single-instance deployment inside its documented storage budget.
        if sum(p.stat().st_size for p in self.root.rglob('*') if p.is_file()) > 500*1024*1024:
            raise ValueError('임시 저장 한도에 도달했습니다. 만료 정리 후 다시 시도하세요.')
        artifact=secrets.token_hex(24);folder=self.root/artifact;folder.mkdir()
        extension='hwp' if kind=='onepage' else 'hwpx'
        name='report.'+extension
        try:
            if kind=='onepage': structural=generate_onepage(ROOT/FILES[kind],folder/name,content)
            else:
                render_hwpx(ROOT/FILES[kind],folder/name,content,kind)
                structural=validate_hwpx(folder/name)
            if not structural['valid']:raise ValueError('생성 파일 구조 검증 실패')
            validation={'input':check,'structure':structural,'template_sha256':TEMPLATE_HASHES[kind]}
            from .integrations import render_pdf
            validation['auto_hwp']=render_pdf(folder/name)
            files={name:None}
            if validation['auto_hwp'].get('rendered'):files['report.pdf']=None
            self.state.put('artifact',artifact,{'owner':owner,'files':list(files),'validation':validation,'expiry':int(time.time())+self.ttl},self.ttl)
            return self.links(artifact,owner)
        except Exception:
            import shutil
            shutil.rmtree(folder)
            raise
