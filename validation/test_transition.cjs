const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../assets/ui_transition.js'), 'utf8');
function setup(supported=true) {
  const listeners={}, timers=new Map(), intervals=new Map(); let id=0, token='old', running=false, calls=0, skipped=0, removed=0, disposed=0, resolved=false;
  const doc={hidden:false, head:{appendChild(){}}, documentElement:{classList:{add(){},remove(){}}},
    getElementById:()=>({remove(){removed++;}}), createElement:()=>({remove(){}}),
    querySelectorAll:()=>[{dataset:{sgRenderToken:token}}], querySelector:()=>running?{}:null,
    addEventListener:(name,fn)=>listeners[name]=fn};
  if(supported) doc.startViewTransition=cb=>{calls++; const done=cb(); done.then(()=>resolved=true); return {ready:Promise.resolve(),finished:done,skipTransition(){skipped++;}};};
  const win={document:doc,AbortController,__sgTransitionDispose:()=>disposed++,
    setInterval:fn=>{intervals.set(++id,fn);return id;},clearInterval:i=>intervals.delete(i),
    setTimeout:(fn,ms)=>{timers.set(++id,{fn,ms});return id;},clearTimeout:i=>timers.delete(i)};
  const context=vm.createContext({window:{parent:win},Promise,Array}); vm.runInContext(code,context);
  function click(text='Duyệt vi phạm',special=false) {
    const button={textContent:text,closest:selector=>selector==='.stApp'?{}:(special?{}:null)};
    listeners.click({target:{closest:()=>button}});
  }
  return {click,win,doc,listeners,timers,intervals,context,token:t=>token=t,running:t=>running=t,
    stats:()=>({calls,skipped,removed,disposed,resolved})};
}
(async()=>{
  let s=setup(); assert.equal(s.stats().disposed,1);assert.equal(s.stats().removed,1);
  s.click(); assert.equal(s.stats().calls,1);s.click();assert.equal(s.stats().calls,1);
  s.token('new');s.running(true);for(const fn of s.intervals.values())fn();assert.equal(s.intervals.size,1);
  s.running(false);for(const fn of [...s.intervals.values()])fn();await Promise.resolve();
  assert.equal(s.stats().resolved,true);assert.equal(s.timers.size,0);assert.equal(s.intervals.size,0);
  s=setup();s.click();assert.equal([...s.timers.values()][0].ms,1500);
  for(const timer of [...s.timers.values()])timer.fn();await Promise.resolve();assert.equal(s.stats().skipped,1);assert.equal(s.stats().resolved,true);
  s=setup(false);s.click();assert.equal(s.stats().calls,0);assert.equal(s.timers.size,0);
  s=setup();s.click('Bắt đầu quét');s.click('Tải xuống');s.click('upload',true);assert.equal(s.stats().calls,0);
  assert.equal(s.listeners.change,undefined);
  s.click();s.doc.hidden=true;s.listeners.visibilitychange();assert.equal(s.stats().skipped,1);
  s=setup();vm.runInContext(code,s.context);assert.equal(s.stats().disposed,1);
  s.click();s.win.__sgTransitionDispose();assert.equal(s.intervals.size,0);assert.equal(s.timers.size,0);
  assert(!code.includes('cloneNode'));assert(!code.includes('attachShadow'));
  console.log('PASS: native transition completion, timeout, unsupported browser, scan/upload exclusions, tab hide, disposal, idempotent install, no DOM cloning.');
})().catch(e=>{console.error(e);process.exit(1);});
