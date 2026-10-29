import ast,math,json,sqlite3,tempfile,datetime
from pathlib import Path
from types import SimpleNamespace
source=Path(__file__).resolve().parents[1]/'core_logic.py'
tree=ast.parse(source.read_text());tree.body=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in {'save_new_violations_to_db','classify_event_status'}]
with tempfile.TemporaryDirectory() as folder:
 root=Path(folder);db=sqlite3.connect(':memory:');db.execute('CREATE TABLE events(id INTEGER PRIMARY KEY,status TEXT)')
 def insert_event(**kw):return db.execute('INSERT INTO events(status) VALUES(?)',(kw['status'],)).lastrowid
 ns=dict(math=math,json=json,EVIDENCE_DIR=root,app_now=lambda:datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=7))),insert_event=insert_event,cv2=SimpleNamespace(imwrite=lambda *a:True),_clear_runtime_caches=lambda:None)
 exec(compile(tree,str(source),'exec'),ns)
 for reason,score,expected in [('helmet_detection_unverified',.82,'pending'),('conflicting_ppe_evidence',.77,'pending'),('negative_not_verified_on_worker_crop',.88,'pending'),(None,.85,'confirmed'),(None,.69,'pending')]:
  v={'label':'NO-Hardhat','confidence':score,'review_reason':reason}
  auto,pending=ns['save_new_violations_to_db']([v],None)
  assert db.execute('SELECT status FROM events ORDER BY id DESC LIMIT 1').fetchone()[0]==expected
  assert bool(auto)==(expected=='confirmed') and bool(pending)==(expected=='pending')
  meta=json.loads((root/f'event_{v["event_ref"]["event_id"]}.json').read_text());assert meta['review_reason']==reason and meta['confidence']==score
print('PASS: uncertain helmet and conflicting PPE persist as pending; verified high scores confirmed; raw scores retained')
