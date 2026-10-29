"""Run without model/Streamlit: exercise production functions with temporary SQLite."""
import ast, math, json, sqlite3, tempfile
from pathlib import Path
from datetime import datetime, timezone
from types import SimpleNamespace
source=Path(__file__).resolve().parents[1]/'core_logic.py'
tree=ast.parse(source.read_text())
names={'classify_event_status','save_new_violations_to_db','MultiPersonTrackerAndDeduplicator','iou_score','box_overlap_ratio'}
tree.body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
ns=dict(math=math,json=json,sqlite3=sqlite3,app_now=lambda:datetime.now(timezone.utc),cv2=SimpleNamespace(imwrite=lambda p,f:Path(p).write_bytes(b'evidence')), _clear_runtime_caches=lambda:None)
exec(compile(tree,str(source),'exec'),ns)
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp); db=root/'events.db'; ns.update(DB_PATH=db,EVIDENCE_DIR=root)
 with sqlite3.connect(db) as con: con.execute('CREATE TABLE events(event_id INTEGER PRIMARY KEY,timestamp TEXT,violation_type TEXT,status TEXT)')
 def insert_event(**v):
  with sqlite3.connect(db) as con:return con.execute('INSERT INTO events(timestamp,violation_type,status) VALUES(?,?,?)',(v['timestamp'],v['violation_type'],v['status'])).lastrowid
 ns['insert_event']=insert_event
 save=ns['save_new_violations_to_db']
 for conf in [.65,.749,.75,.76,.83]:
  for reason in [None,'vest_confidence_not_stable','conflicting_ppe_evidence','negative_not_verified_on_worker_crop']:
   v=dict(label='NO-Safety Vest',confidence=conf,worker_id=1,review_reason=reason)
   auto,pending=save([v],None)
   assert bool(auto)==(conf>=.75)
   assert bool(pending)==(conf<.75)
   # Retrying the same record must never insert a second row.
   with sqlite3.connect(db) as con:before=con.execute('SELECT count(*) FROM events').fetchone()[0]
   assert save([v],None)==([],[])
   with sqlite3.connect(db) as con:assert con.execute('SELECT count(*) FROM events').fetchone()[0]==before
 v=dict(label='NO-Safety Vest',confidence=.65,worker_id=9,review_reason='conflicting_ppe_evidence')
 _,pending=save([v],None);eid=pending[0]['event_id'];v['confidence']=.83
 auto,pending=save([v],None);assert len(auto)==1 and auto[0]['event_id']==eid and auto[0]['upgraded_from_pending']
 with sqlite3.connect(db) as con:con.execute("UPDATE events SET status='false_positive' WHERE event_id=?",(eid,))
 assert save([v],None)==([],[])
 with sqlite3.connect(db) as con:assert con.execute('SELECT status FROM events WHERE event_id=?',(eid,)).fetchone()[0]=='false_positive'
T=ns['MultiPersonTrackerAndDeduplicator'];p={'bbox':[100,100,200,300],'confidence':.9}
t=T();first=t.update_workers([p],0,1000,800)[0]['worker_id'];t.mark_logged(first,'NO-Safety Vest',(150,200),0)
t._event_refs={(first,'NO-Safety Vest'):{'event_id':12,'status':'pending'}}
t.update_workers([],100,1000,800)
second=t.update_workers([p],150,1000,800)[0]['worker_id'];assert first==second
assert t.is_already_logged(second,'NO-Safety Vest',(150,200),1000,800,150)
assert t._event_refs[(second,'NO-Safety Vest')]['event_id']==12
# Two distant workers remain independent; a new scan has independent IDs/locks.
people=t.update_workers([p,{'bbox':[700,100,800,300],'confidence':.9}],155,1000,800)
assert len({x['worker_id'] for x in people})==2
assert not T().logged_worker_violations
# After a long absence we cannot safely assert identity: do not merge strangers.
t.update_workers([],1000,1000,800);assert t.update_workers([p],1010,1000,800)[0]['worker_id']!=first
print('PASS: threshold boundaries and diagnostic reasons; idempotent writes; pending upgrade same ID; human decisions; short occlusion and distinct workers.')
import sys
sys.path.insert(0,str(source.parent))
from repair_pending_status import repair
with tempfile.TemporaryDirectory() as tmp:
 root=Path(tmp);db=root/'events.db'
 with sqlite3.connect(db) as con:
  con.execute('CREATE TABLE events(event_id INTEGER PRIMARY KEY,status TEXT)')
  for eid,score,origin,status in [(1,.83,'ai_pending','pending'),(2,.76,'ai_pending','pending'),(3,.65,'ai_pending','pending'),(4,.9,'human','pending'),(5,.9,'ai_pending','false_positive')]:
   con.execute('INSERT INTO events VALUES(?,?)',(eid,status))
   (root/f'event_{eid}.json').write_text(json.dumps(dict(confidence=score,status_origin=origin,triage_rule='verified_confidence_or_review_reason_v9')))
 ids,backup=repair(db,root);assert ids==[1,2] and backup.is_dir()
 assert repair(db,root)==([],None)
 with sqlite3.connect(backup/db.name) as con:assert con.execute("SELECT count(*) FROM events WHERE status='pending'").fetchone()[0]==4
print('PASS: legacy status repair, backup, repeat run and human/rejected decision protection.')
