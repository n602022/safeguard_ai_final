"""Exercise detection -> pending SQLite event -> later-frame automatic upgrade."""
import tempfile,sqlite3,json,pathlib
import test_rules as rules
ns=rules.ns
with tempfile.TemporaryDirectory() as directory:
 root=pathlib.Path(directory);dbpath=root/'events.db'
 with sqlite3.connect(dbpath) as db:
  db.execute('CREATE TABLE events(event_id INTEGER PRIMARY KEY,timestamp TEXT,violation_type TEXT,status TEXT)')
 def insert_event(**kw):
  with sqlite3.connect(dbpath) as db:
   return db.execute('INSERT INTO events(timestamp,violation_type,status) VALUES(?,?,?)',(kw['timestamp'],kw['violation_type'],kw['status'])).lastrowid
 ns.update(DB_PATH=dbpath,sqlite3=sqlite3,EVIDENCE_DIR=root,insert_event=insert_event)
 tracker=ns['MultiPersonTrackerAndDeduplicator']()
 rules.set_dets([rules.p,('NO-Hardhat',.69,[115,30,150,65])])
 events=[]
 for i in range(0,40,5):events+=rules.run(tracker,i,False)
 assert len(events)==1
 auto,pending=ns['save_new_violations_to_db'](events,rules.f)
 assert len(pending)==1 and not auto
 eid=pending[0]['event_id']
 rules.set_dets([rules.p,('NO-Hardhat',.85,[115,30,150,65])])
 events=rules.run(tracker,40,False)
 assert len(events)==1 and events[0]['upgrade_event_id']==eid
 auto,pending=ns['save_new_violations_to_db'](events,rules.f,frame_idx=40)
 assert len(auto)==1 and not pending and auto[0]['upgraded_from_pending']
 with sqlite3.connect(dbpath) as db:
  assert db.execute('SELECT count(*) FROM events').fetchone()[0]==1
  assert db.execute('SELECT status FROM events').fetchone()[0]=='confirmed'
 meta=json.loads((root/f'event_{eid}.json').read_text())
 assert meta['confidence']==.85 and meta['initial_status']=='pending'
 assert meta['frame_idx']==40 and meta['status_origin']=='ai_auto'
 assert not rules.run(tracker,45,False),'must not repeat confirmed event'
 # Protect both human-origin metadata and database decisions from an AI retry.
 for origin,status in [('human','pending'),('ai_pending','false_positive')]:
  meta['status_origin']=origin;(root/f'event_{eid}.json').write_text(json.dumps(meta))
  with sqlite3.connect(dbpath) as db:db.execute('UPDATE events SET status=?',(status,))
  assert ns['save_new_violations_to_db'](events,rules.f)==([],[])
  with sqlite3.connect(dbpath) as db:assert db.execute('SELECT status FROM events').fetchone()[0]==status
print('PASS: 69% pending -> 85% confirmed on same event; evidence and counts agree; human decisions protected')
