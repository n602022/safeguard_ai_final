import tempfile,pathlib,sys,shutil,os,importlib
with tempfile.TemporaryDirectory() as directory:
 root=pathlib.Path(directory)
 shutil.copy(pathlib.Path(__file__).parents[1]/'runtime_loader.py',root/'runtime_loader.py')
 (root/'core_logic.py').write_text('def label(): return "OLD"\n')
 (root/'ui_pages').mkdir();(root/'ui_pages/__init__.py').write_text('')
 (root/'ui_pages/scanner.py').write_text('from core_logic import label\n')
 sys.path.insert(0,directory)
 import runtime_loader,core_logic
 from ui_pages import scanner
 runtime_loader.refresh_project_modules()
 assert scanner.label()=='OLD'
 source=root/'core_logic.py';stat=source.stat();source.write_text('def label(): return "NEW"\n');os.utime(source,ns=(stat.st_atime_ns,stat.st_mtime_ns))
 runtime_loader.refresh_project_modules()
 assert scanner.label()=='NEW','consumer retained stale function'
 identity=scanner.label
 runtime_loader.refresh_project_modules()
 assert scanner.label is identity,'unchanged rerun must not reload modules'
 print('PASS: source edits refresh imported functions, even same size/timestamp; unchanged reruns do not reload')
