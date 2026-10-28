"""Status regression tests against real temporary SQLite + evidence JSON."""
import ast, pathlib, tempfile, sqlite3, json, datetime, math
import cv2, numpy as np
import sys
sys.path.insert(0,str(__import__('pathlib').Path(__file__).resolve().parents[1]))
from app_clock import app_now

root=pathlib.Path(__file__).resolve().parents[1]
tree=ast.parse((root/'core_logic.py').read_text())
selected={'classify_event_status','save_new_violations_to_db','update_event_status','get_effective_auto_confirm'}
tree.body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in selected]
with tempfile.TemporaryDirectory() as directory:
 evidence=pathlib.Path(directory);db=sqlite3.connect(':memory:')
 db.execute('CREATE TABLE events(event_id INTEGER PRIMARY KEY, timestamp TEXT, violation_type TEXT, status TEXT)')
 def insert_event(timestamp,violation_type,status):
  return db.execute('INSERT INTO events(timestamp,violation_type,status) VALUES(?,?,?)',(timestamp,violation_type,status)).lastrowid
 def update(event_id,new_status):
  return db.execute('UPDATE events SET status=? WHERE event_id=?',(new_status,event_id)).rowcount>0
 from types import SimpleNamespace
 ns=dict(app_now=app_now,math=math,cv2=cv2,np=np,datetime=datetime,json=json,EVIDENCE_DIR=evidence,insert_event=insert_event,_db_update_event_status=update,_clear_runtime_caches=lambda:None,st=SimpleNamespace(session_state={'ai_sensitivity':.85,'auto_confirm_level':.75}))
 exec(compile(tree,'policy','exec'),ns)
 assert ns['get_effective_auto_confirm']()==.75,'no hidden threshold increase'
 for score,threshold,expected in [(.69,.75,'pending'),(.7499,.75,'pending'),(.75,.75,'confirmed'),(.85,.75,'confirmed'),(.88,.75,'confirmed'),(.85,.90,'pending')]:
  for label in ['NO-Hardhat','NO-Safety Vest']:
   ns['save_new_violations_to_db']([{'label':label,'confidence':score,'auto_confirm_eligible':False,'verification_score':.1}],np.zeros((24,24,3),np.uint8),auto_confirm_threshold=threshold)
   eid,status=db.execute('SELECT event_id,status FROM events ORDER BY event_id DESC LIMIT 1').fetchone()
   assert status==expected,(score,threshold,status)
   meta=json.loads((evidence/f'event_{eid}.json').read_text())
   assert meta['auto_triaged']==(expected=='confirmed')
   assert meta['confidence']==score
   assert meta['status_origin']==('ai_auto' if expected=='confirmed' else 'ai_pending')
 # A reviewer may legitimately confirm a 69% event; that is not AI auto-confirmation.
 ns['update_event_status'](1,'confirmed')
 meta=json.loads((evidence/'event_1.json').read_text())
 assert meta['status_origin']=='human' and meta['auto_triaged'] is False
 assert meta['initial_status']=='pending' and meta['current_status']=='confirmed'
 assert db.execute('SELECT status FROM events WHERE event_id=1').fetchone()[0]=='confirmed'
 try: ns['update_event_status'](999,'confirmed')
 except ValueError: pass
 else: raise AssertionError('missing event must not show success')
 for bad in [float('nan'),float('inf'),-1,1.1]:
  try: ns['classify_event_status'](bad,.75)
  except ValueError: pass
  else: raise AssertionError('invalid confidence')
print('PASS: 12 SQLite triage cases; threshold equality/boundary; no hidden threshold; confidence persistence; manual decision origin; missing event; invalid scores')
