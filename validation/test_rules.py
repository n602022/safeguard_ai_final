import ast,math
from types import SimpleNamespace
import cv2,numpy as np
s=ast.parse(open(str(__import__('pathlib').Path(__file__).resolve().parents[1] / 'core_logic.py')).read());names={'box_overlap_ratio','iou_score','box_inclusion_ratio','is_anatomically_valid','evaluate_lighting_and_glare','MultiPersonTrackerAndDeduplicator','_draw_smart_label','smart_detect_and_annotate'};s.body=[n for n in s.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
ns={'math':math,'cv2':cv2,'np':np};exec(compile(s,'core','exec'),ns)
labels=['Person','NO-Hardhat','Hardhat','NO-Safety Vest','Safety Vest']
def set_dets(ds):
 boxes=[SimpleNamespace(cls=np.array(labels.index(l)),conf=np.array(c),xyxy=np.array([b])) for l,c,b in ds]
 ns['_model']=SimpleNamespace(predict=lambda **kw:[SimpleNamespace(boxes=boxes,names=labels)])
f=np.random.default_rng(42).integers(65,225,(300,300,3),dtype=np.uint8)
p=('Person',.9,[80,25,200,280]);v=('NO-Hardhat',.9,[115,30,150,65])
def run(tracker=None,idx=1,single=True):return ns['smart_detect_and_annotate'](f,tracker=tracker,frame_idx=idx,single_frame_mode=single)[1]
set_dets([v]);assert not run(),'orphan'
set_dets([p,v,('Hardhat',.3,[110,27,155,65])]);assert not run(),'low confidence PPE must veto'
set_dets([p,v]);assert len(run())==1,'positive image control'
t=ns['MultiPersonTrackerAndDeduplicator']()
for i in range(0,35,5): assert not run(t,i,False)
vs=run(t,35,False);assert len(vs)==1 and vs[0]['auto_confirm_eligible']
assert not run(t,40,False),'duplicate'
set_dets([p,('NO-Hardhat',.8,[115,30,150,65])])
t=ns['MultiPersonTrackerAndDeduplicator']()
for i in range(0,35,5):assert not run(t,i,False)
assert not run(t,35,False)[0]['auto_confirm_eligible'],'weak evidence must remain pending'
set_dets([p,v]); assert not run()[0]['auto_confirm_eligible'],'single image must remain pending'
t=ns['MultiPersonTrackerAndDeduplicator']()
for i in [0,5,10]: assert not run(t,i,False)
set_dets([p]);assert not run(t,15,False)
set_dets([p,v])
for i in [20,25,30,35,40,45,50]:assert not run(t,i,False),'missing frame must reset support'
assert run(t,55,False)[0]['auto_confirm_eligible']
original_frame=f
f=np.full((300,300,3),30,dtype=np.uint8)
t=ns['MultiPersonTrackerAndDeduplicator']()
for i in range(0,35,5):assert not run(t,i,False)
assert not run(t,35,False)[0]['auto_confirm_eligible'],'blur/low light must block auto-confirm'
f=original_frame
set_dets([p,v]);t=ns['MultiPersonTrackerAndDeduplicator']()
for i in [0,5,10]:assert not run(t,i,False)
set_dets([p,v,('Hardhat',.4,[110,27,155,65])]);assert not run(t,15,False)
set_dets([p,v])
for i in [20,25,30,35,40,45,50]:assert not run(t,i,False)
assert run(t,55,False)[0]['auto_confirm_eligible']
# Exercise persistence policy with temporary evidence and an in-memory insert stub.
import tempfile, pathlib, datetime, json
saved=[]
ns.update(datetime=datetime,json=json,EVIDENCE_DIR=pathlib.Path(tempfile.mkdtemp()),insert_event=lambda **kw: saved.append(kw) or len(saved),_clear_runtime_caches=lambda:None)
tree=ast.parse(open(str(pathlib.Path(__file__).resolve().parents[1] / 'core_logic.py')).read())
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='save_new_violations_to_db')
exec(compile(ast.Module(body=[node],type_ignores=[]),'save','exec'),ns)
ns['save_new_violations_to_db'](vs,f,auto_confirm_threshold=.75)
assert saved[-1]['status']=='confirmed'
ns['save_new_violations_to_db'](vs,f,auto_confirm_threshold=.95)
assert saved[-1]['status']=='pending'
print('PASS: PPE veto, orphan rejection, positive image, temporal auto-confirm, lower confidence pending, single image pending, missing support reset, duplicate suppression, database status threshold')
