(() => {
  let win, doc;
  try {win=window.parent;doc=win.document;} catch (_) {return;}
  if(win.__sgTransitionVersion === 11) return;
  if(win.__sgTransitionDispose) win.__sgTransitionDispose();
  doc.getElementById('sg-transition-snapshot')?.remove();
  win.__sgTransitionVersion=11;
  const controller = new win.AbortController();
  const tokens=()=>Array.from(doc.querySelectorAll('[data-sg-render-token]')).map(el=>el.dataset.sgRenderToken).join('|');
  let beforeTokens='';
  let overlay=null,quiet=null,watchdog=null,started=0;
  const running=()=>!!doc.querySelector('.stApp[data-teststate="running"]');
  const release=()=>{if(overlay){overlay.remove();overlay=null;}win.clearTimeout(quiet);win.clearTimeout(watchdog);};
  const settle=()=>{
    if(!overlay)return;
    win.clearTimeout(quiet);
    quiet=win.setTimeout(()=>{
      if(tokens()!==beforeTokens && !running() && Date.now()-started>180)release();
      else if(overlay)settle();
    },120);
  };
  const freeze=()=>{
    if(overlay)return;
    beforeTokens=tokens();
    const app=doc.querySelector('.stApp');if(!app)return;
    const clone=app.cloneNode(true);
    const originals=[app,...app.querySelectorAll('*')];
    const copies=[clone,...clone.querySelectorAll('*')];
    overlay=doc.createElement('div');overlay.id='sg-transition-snapshot';
    overlay.setAttribute('aria-hidden','true');
    overlay.style.cssText='position:fixed;inset:0;z-index:999990;overflow:hidden;pointer-events:auto;';
    const shadow=overlay.attachShadow({mode:'open'});
    doc.querySelectorAll('style,link[rel="stylesheet"]').forEach(el=>shadow.appendChild(el.cloneNode(true)));
    const vars=win.getComputedStyle(app);
    for(let i=0;i<vars.length;i++){const key=vars[i];if(key.startsWith('--'))overlay.style.setProperty(key,vars.getPropertyValue(key));}
    clone.style.margin='0';shadow.appendChild(clone);doc.body.appendChild(overlay);
    originals.forEach((el,i)=>{if(copies[i]){copies[i].scrollTop=el.scrollTop;copies[i].scrollLeft=el.scrollLeft;}});
    started=Date.now();watchdog=win.setTimeout(release,10000);settle();
  };
  doc.addEventListener('click',event=>{
    const button=event.target.closest('button');if(!button)return;
    // Live scan must stream its frames. Native pickers/downloads need no mask.
    if(/Bắt đầu quét|Dừng quét|Browse|Tải bằng chứng|Xuất báo cáo|Tải xuống/i.test(button.textContent||''))return;
    if(button.closest('[data-testid="stFileUploader"],#sg-transition-snapshot'))return;
    freeze();
  },{capture:true,signal:controller.signal});
  doc.addEventListener('change',event=>{
    if(event.target.matches('input[type="file"]'))return;
    if(event.target.closest('.stApp'))freeze();
  },{capture:true,signal:controller.signal});
  const observer=new win.MutationObserver(settle);
  observer.observe(doc.querySelector('#root')||doc.body,{childList:true,subtree:true,attributes:true,attributeFilter:['data-teststate']});
  doc.addEventListener('visibilitychange',()=>{if(doc.hidden)release();},{signal:controller.signal});
  win.__sgTransitionDispose=()=>{release();controller.abort();observer.disconnect();};
})();
