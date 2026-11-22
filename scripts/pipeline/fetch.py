# Fetch URLs via the n8n page gateway (fo-page-fetch-x81k2), cache per URL (resumable).
import json,os,subprocess,threading,time
from concurrent.futures import ThreadPoolExecutor
CACHE=os.environ.get('FETCH_CACHE','pages.jsonl')
URL='https://exaltisgroup.app.n8n.cloud/webhook/fo-page-fetch-x81k2'
lock=threading.Lock()
def cached():
    got={}
    if os.path.exists(CACHE):
        for ln in open(CACHE):
            try: r=json.loads(ln); got[r['url_req']]=r
            except Exception: pass
    return got
def call(batch):
    body=json.dumps({'lean':True,'batch':[{'tag':str(i),'url':u} for i,u in enumerate(batch)]})
    for a in range(3):
        p=subprocess.run(['curl','-sS','-m','280','-X','POST','-H','Content-Type: application/json','--data-binary','@-',URL],input=body.encode(),capture_output=True)
        try:
            d=json.loads(p.stdout); data=d['data'] if isinstance(d.get('data'),list) else [d['data']]
            out=[]
            for x in data:
                i=int(x.get('tag')); x.pop('html',None); x['url_req']=batch[i]; out.append(x)
            return out
        except Exception: time.sleep(5)
    return [{'url_req':u,'err':'gateway_fail','text':'','emails':[],'links':[]} for u in batch]
def run(urls,bs=25,workers=6,refetch_errors=False):
    got=cached()
    todo=[u for u in dict.fromkeys(urls) if u not in got or (refetch_errors and got[u].get('err'))]
    chunks=[todo[i:i+bs] for i in range(0,len(todo),bs)]
    def job(c):
        res=call(c)
        with lock:
            with open(CACHE,'a') as f:
                for r in res: f.write(json.dumps(r)+'\n')
    with ThreadPoolExecutor(workers) as ex: list(ex.map(job,chunks))
    return cached()
