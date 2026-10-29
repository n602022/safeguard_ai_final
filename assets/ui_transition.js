(() => {
  let win, doc;
  try { win = window.parent; doc = win.document; } catch (_) { return; }
  if (win.__sgTransitionVersion === 12) return;
  if (typeof win.__sgTransitionDispose === 'function') win.__sgTransitionDispose();
  doc.getElementById('sg-transition-snapshot')?.remove();
  win.__sgTransitionVersion = 12;
  const controller = new win.AbortController();
  let active = null;
  const style = doc.createElement('style');
  style.textContent = `
    html.sg-transition-active::view-transition-group(root),
    html.sg-transition-active::view-transition-old(root),
    html.sg-transition-active::view-transition-new(root) {
      animation: none !important;
    }
  `;
  doc.head.appendChild(style);
  const tokens = () => Array.from(doc.querySelectorAll('[data-sg-render-token]'))
    .map(el => el.dataset.sgRenderToken).join('|');
  const finish = (state, skip = false) => {
    if (!state || active !== state) return;
    active = null;
    win.clearInterval(state.poll);
    win.clearTimeout(state.timeout);
    state.resolve();
    if (skip) state.transition?.skipTransition();
    // Keep transition CSS until the browser releases its native snapshot.
    Promise.resolve(state.transition?.finished).catch(() => {}).finally(() => {
      if (!active) doc.documentElement.classList.remove('sg-transition-active');
    });
  };
  const begin = () => {
    // Unsupported browsers retain normal Streamlit rendering, with no overlay.
    if (active || doc.hidden || typeof doc.startViewTransition !== 'function') return;
    const before = tokens();
    if (!before || doc.querySelector('.stApp[data-teststate="running"]')) return;
    let resolve;
    const done = new Promise(r => { resolve = r; });
    const state = { resolve, transition: null, poll: null, timeout: null };
    active = state;
    doc.documentElement.classList.add('sg-transition-active');
    try {
      state.transition = doc.startViewTransition(() => done);
      state.transition.ready.catch(() => finish(state, true));
      state.transition.finished.catch(() => {}).finally(() => finish(state));
      state.poll = win.setInterval(() => {
        if (tokens() !== before && !doc.querySelector('.stApp[data-teststate="running"]')) {
          finish(state);
        }
      }, 40);
      // Never hold an old screen for the previous 10-second watchdog.
      state.timeout = win.setTimeout(() => finish(state, true), 1500);
    } catch (_) { finish(state, true); }
  };
  doc.addEventListener('click', event => {
    const button = event.target.closest?.('button');
    if (!button || button.disabled || !button.closest('.stApp')) return;
    if (button.closest('[data-testid="stFileUploader"],[data-testid="stDownloadButton"]')) return;
    if (/Bắt đầu quét|Dừng quét|Browse|Tải bằng chứng|Xuất báo cáo|Tải xuống/i.test(button.textContent || '')) return;
    begin();
  }, { capture: true, signal: controller.signal });
  // Do not freeze every input/change event: sliders, uploads and scan streams
  // must remain interactive and do not necessarily produce a page-end marker.
  doc.addEventListener('visibilitychange', () => {
    if (doc.hidden) finish(active, true);
  }, { signal: controller.signal });
  win.__sgTransitionDispose = () => {
    finish(active, true);
    controller.abort();
    style.remove();
  };
})();
