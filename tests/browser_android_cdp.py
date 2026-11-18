"""Minimal direct page CDP adapter for Android WebViews without browser contexts."""
import json,os,time,urllib.request
from websockets.sync.client import connect


class RawPage:
    def __init__(self,endpoint='http://127.0.0.1:9222'):
        targets=json.load(urllib.request.urlopen(endpoint+'/json',timeout=10))
        target=next(t for t in targets if t.get('type')=='page')
        self.ws=connect(target['webSocketDebuggerUrl'],max_size=64*1024*1024,open_timeout=10)
        self.counter=0;self.timeout=120;self.listeners={}
        self.call('Runtime.enable',{})
    def call(self,method,params):
        self.counter+=1;request_id=self.counter
        if os.environ.get('ASTERION_CDP_VERBOSE')=='1':
            expression=str(params.get('expression',''))
            print('CDP',request_id,method,expression[:60],expression[-80:] if len(expression)>60 else '',flush=True)
        self.ws.send(json.dumps({'id':request_id,'method':method,'params':params}))
        while True:
            result=json.loads(self.ws.recv(timeout=360))
            if result.get('id')==request_id:
                if 'error' in result:raise RuntimeError(result['error'])
                return result.get('result',{})
            if result.get('method')=='Runtime.exceptionThrown':
                for callback in self.listeners.get('pageerror',[]):callback(result.get('params'))
    def on(self,event,callback):self.listeners.setdefault(event,[]).append(callback)
    def set_default_timeout(self,milliseconds):self.timeout=milliseconds/1000
    def evaluate(self,expression,arg=None):
        stripped=expression.strip()
        if arg is not None:expression=f'({expression})({json.dumps(arg)})'
        elif stripped.startswith(('async','()=>','() =>','function')):expression=f'({expression})()'
        result=self.call('Runtime.evaluate',{'expression':expression,'awaitPromise':True,'returnByValue':True})
        if result.get('exceptionDetails'):raise RuntimeError(result['exceptionDetails'])
        return result.get('result',{}).get('value')
    def wait_for_function(self,expression,timeout=None):
        deadline=time.monotonic()+(timeout/1000 if timeout else self.timeout)
        while time.monotonic()<deadline:
            if self.evaluate(expression):return
            time.sleep(1)
        raise TimeoutError(expression)
    def wait_for_selector(self,selector):self.locator(selector).wait_for()
    def wait_for_timeout(self,milliseconds):time.sleep(milliseconds/1000)
    def locator(self,selector):return RawLocator(self,selector)


class RawLocator:
    def __init__(self,page,selector):self.page=page;self.selector=selector
    def evaluate(self,function):return self.page.evaluate(f'({function})(document.querySelector({json.dumps(self.selector)}))')
    def count(self):return self.page.evaluate(f'document.querySelectorAll({json.dumps(self.selector)}).length')
    def is_visible(self):return self.evaluate('(el)=>!!el&&!!el.getClientRects().length&&getComputedStyle(el).visibility!=="hidden"')
    def wait_for(self,state='visible'):
        deadline=time.monotonic()+self.page.timeout
        while time.monotonic()<deadline:
            if self.is_visible():return
            time.sleep(1)
        raise TimeoutError(self.selector)
    def scroll_into_view_if_needed(self):self.evaluate('(el)=>el.scrollIntoView({block:"center",inline:"nearest"})')
    def bounding_box(self):return self.evaluate('(el)=>{const b=el.getBoundingClientRect();return {x:b.x,y:b.y,width:b.width,height:b.height}}')
    def fill(self,value):self.evaluate('(el)=>{el.value='+json.dumps(value)+';el.dispatchEvent(new Event("input",{bubbles:true}));}')
    def input_value(self):return self.evaluate('(el)=>el.value')
    def inner_text(self):return self.evaluate('(el)=>el.innerText')
