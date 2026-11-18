"""Exercise native bridge message ordering using a deterministic fake Java host.
The real interpreter/process is tested separately on the Android emulator.
"""
from pathlib import Path
import functools,http.server,json,shutil,threading
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT/'web')))
threading.Thread(target=server.serve_forever,daemon=True).start()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=shutil.which('chromium'),headless=True,args=['--no-sandbox'])
  page=browser.new_page()
  page.route('**/bridge-test.html',lambda r:r.fulfill(content_type='text/html',body='<html><body>Bridge test</body></html>'))
  page.goto(f'http://127.0.0.1:{server.server_port}/bridge-test.html')
  results=page.evaluate('''async()=>{
   const calls=[]; let failInit=false;
   const emit=event=>window.onNativePythonMessage(JSON.stringify(event));
   window.Android={
    pythonInit(id){calls.push({type:'init',id});setTimeout(()=>emit(failInit?{type:'init-error',requestId:id,message:'INIT FAILURE'}:{type:'ready',requestId:id,pythonVersion:'3.12.15'}),0);},
    pythonRun(id,exerciseId,code,variant,timeoutMs){
     calls.push({type:'run',id,exerciseId,code,variant,timeoutMs});
     if(code==='never')return;
     setTimeout(()=>{
      if(code==='timeout'){emit({type:'reset',message:'process stopped'});emit({type:'result',requestId:id,result:{status:'timeout',checks:[],feedback:'timeout'}});}
      else if(code==='system-error')emit({type:'init-error',requestId:id,message:'SERVICE FAILURE'});
      else emit({type:'result',requestId:id,result:{status:'passed',phase:'execution',stdout:'native stdout',stderr:'',checks:[],feedback:'ok',artifact:{label:'actual',input:'x',output:'42'}}});
     },0);
    },
    pythonStop(id){calls.push({type:'stop',id});emit({type:'reset',message:'stop'});}
   };
   const {PythonRunner}=await import('/js/python-runner.js');
   const runner=new PythonRunner();
   const good=await runner.run({exerciseId:'p01',code:'print("лес")',variant:'transfer',timeoutMs:4321});
   const timeout=await runner.run({exerciseId:'p01',code:'timeout'});
   const recovered=await runner.run({exerciseId:'p01',code:'ok'});
   const pending=runner.run({exerciseId:'p01',code:'never'});
   await new Promise(r=>setTimeout(r,10));runner.stop();const stopped=await pending;
   // A stale completion from the killed process must not affect the next run.
   const killed=calls.filter(x=>x.type==='run').at(-1).id;
   emit({type:'result',requestId:killed,result:{status:'passed'}});
   failInit=true;const initError=await runner.run({exerciseId:'p01',code:'ok'});failInit=false;
   const afterError=await runner.run({exerciseId:'p01',code:'ok'});
   const systemError=await runner.run({exerciseId:'p01',code:'system-error'});
   const other=new PythonRunner();const otherGood=await other.run({exerciseId:'p02',code:'ok'});
   runner.stop();other.stop();
   return {good,timeout,recovered,stopped,initError,afterError,systemError,otherGood,calls};
  }''')
  browser.close()
 assert results['good']['status']=='passed'
 assert results['good']['artifact']['output']=='42'
 assert results['timeout']['status']=='timeout',results['timeout']
 assert results['recovered']['status']==results['afterError']['status']==results['otherGood']['status']=='passed'
 assert results['stopped']['status']=='cancelled'
 assert results['initError']['status']=='error' and results['initError']['phase']=='initialization'
 assert results['systemError']['phase']=='initialization'
 run=next(x for x in results['calls'] if x['type']=='run')
 assert run['code']=='print("лес")' and run['variant']=='transfer' and run['timeoutMs']==4321
 request_ids=[x['id'] for x in results['calls'] if x['type']!='stop']
 assert len(request_ids)==len(set(request_ids))
 report={'passed':True,'bridgeSelection':True,'unicodeAndVariant':True,'requestCorrelation':True,
         'timeoutResetOrdering':True,'cancelAndStaleReply':True,'initializationErrorPhase':True,'recovery':True}
 (ROOT/'artifacts/native-adapter-tests.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
finally:server.shutdown()
