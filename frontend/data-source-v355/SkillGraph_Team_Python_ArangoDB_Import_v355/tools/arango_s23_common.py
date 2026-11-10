"""Shared minimal ArangoDB HTTP client. Standard Python only; no network until called."""
import base64
import getpass
import json
import os
import pathlib
import urllib.error
import urllib.parse
import urllib.request

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ArangoError(RuntimeError):
    pass

class ArangoHTTP:
    def __init__(self, base='http://127.0.0.1:8529', username='root', password=None):
        self.base=base.rstrip('/')
        self.username=username
        self.password=getpass.getpass('ArangoDB password (input hidden): ') if password is None else password

    def request(self, method, path, payload=None, content_type='application/json'):
        if isinstance(payload,(dict,list)):
            body=json.dumps(payload,ensure_ascii=False).encode('utf8')
        else:
            body=payload
        token=base64.b64encode(f'{self.username}:{self.password}'.encode('utf8')).decode('ascii')
        headers={'Authorization':'Basic '+token,'Accept':'application/json'}
        if body is not None: headers['Content-Type']=content_type
        req=urllib.request.Request(self.base+path,data=body,method=method,headers=headers)
        try:
            with urllib.request.urlopen(req,timeout=60) as r:
                data=r.read().decode('utf8')
                result=json.loads(data) if data else {}
                if result.get('error'):raise ArangoError(f'{method} {path}: {result.get("errorMessage",result)}')
                return result
        except urllib.error.HTTPError as e:
            try: msg=json.loads(e.read().decode('utf8')).get('errorMessage','unknown error')
            except Exception:msg='unknown error'
            raise ArangoError(f'{method} {path} → HTTP {e.code}: {msg}') from e
        except urllib.error.URLError as e:
            raise ArangoError(f'Cannot connect to {self.base}: {e.reason}') from e

    def dbpath(self,db,suffix):
        return '/_db/'+urllib.parse.quote(db,safe='')+suffix

    def aql(self,db,query,bind_vars=None):
        all_rows=[]
        payload={'query':query,'bindVars':bind_vars or {},'batchSize':1000}
        result=self.request('POST',self.dbpath(db,'/_api/cursor'),payload)
        all_rows.extend(result.get('result',[]))
        while result.get('hasMore'):
            cur=urllib.parse.quote(result['id'],safe='')
            result=self.request('PUT',self.dbpath(db,'/_api/cursor/'+cur),{})
            all_rows.extend(result.get('result',[]))
        return all_rows

def release_counts():
    root=ROOT/'release'
    doc={}
    for p in sorted(root.rglob('*.jsonl')):
        doc[p.stem]=sum(bool(line.strip()) for line in p.open(encoding='utf8'))
    return doc
