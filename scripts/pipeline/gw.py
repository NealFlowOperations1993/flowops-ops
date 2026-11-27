# Smartlead API through the n8n gateway (fo-smartlead-gateway-5h2w). Publish the gateway only while in use.
import json,subprocess,sys,time
URL='https://exaltisgroup.app.n8n.cloud/webhook/fo-smartlead-gateway-5h2w'
def call(batch):
    out=[]
    for i in range(0,len(batch),30):
        body=json.dumps({'batch':batch[i:i+30]})
        for a in range(3):
            p=subprocess.run(['curl','-sS','-m','300','-X','POST','-H','Content-Type: application/json','--data-binary','@-',URL],input=body.encode(),capture_output=True)
            try: out+=json.loads(p.stdout)['results']; break
            except Exception: print('retry',p.stdout[:200],file=sys.stderr); time.sleep(5)
    return out
