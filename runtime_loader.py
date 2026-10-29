"""Refresh project modules after source edits, before page functions are imported."""
import hashlib
import importlib
from pathlib import Path
import sys
import threading
_lock = threading.RLock()
_signatures = {}
_ORDER = ('app_clock','video_processor','detector','core_logic','ui_theme','ui_transition',
          'ui_components','ui_pages.dashboard','ui_pages.scanner','ui_pages.review',
          'ui_pages.assistant','ui_pages.documents')
def refresh_project_modules():
    base = Path(__file__).resolve().parent
    with _lock:
        signatures = {}
        for name in _ORDER:
            path = base.joinpath(*name.split('.')).with_suffix('.py')
            if path.is_file(): signatures[name] = hashlib.sha256(path.read_bytes()).hexdigest()
        changed = {name for name, digest in signatures.items() if _signatures.get(name) != digest}
        if not changed: return
        importlib.invalidate_caches()
        dirty = False
        for name in _ORDER:
            dirty = dirty or name in changed
            module = sys.modules.get(name)
            if dirty and module is not None:
                origin = getattr(module, '__file__', None)
                if origin and Path(origin).resolve().is_relative_to(base):
                    # Source fingerprints also catch edits within one timestamp
                    # tick; discard bytecode that Python might otherwise reuse.
                    cached = getattr(module, '__cached__', None)
                    if cached:
                        try: Path(cached).unlink(missing_ok=True)
                        except OSError: pass
                    importlib.reload(module)
        _signatures.update(signatures)
        core = sys.modules.get('core_logic')
        if core is not None:
            print('SafeGuard active core:', getattr(core, '__file__', '?'),
                  '| source:', signatures.get('core_logic', '?')[:12], flush=True)
