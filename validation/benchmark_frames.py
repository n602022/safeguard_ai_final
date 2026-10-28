import ast, pathlib, math, json, time
import cv2, numpy as np, torch
from ultralytics import YOLO
torch.set_num_threads(2)
import argparse
parser=argparse.ArgumentParser()
parser.add_argument('--inputs',required=True,help='Folder containing original test images and sample videos')
parser.add_argument('--model',required=True)
parser.add_argument('--original-core',required=True)
args=parser.parse_args()
model=YOLO(args.model)
def load(path):
 tree=ast.parse(pathlib.Path(path).read_text())
 names={'box_overlap_ratio','iou_score','box_inclusion_ratio','is_anatomically_valid','evaluate_lighting_and_glare','MultiPersonTrackerAndDeduplicator','_draw_smart_label','smart_detect_and_annotate','refine_distant_detections','refine_weak_ppe_detections'}
 tree.body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names]
 ns={'math':math,'cv2':cv2,'np':np,'_model':model};exec(compile(tree,path,'exec'),ns);return ns
old=load(args.original_core);new=load(str(pathlib.Path(__file__).resolve().parents[1]/'core_logic.py'))
rows=[]
def evaluate(frame,name):
 row={'source':name}
 for key,ns in [('original',old),('patched',new)]:
  kw={'single_frame_mode':True} if key=='patched' else {}
  t=time.perf_counter();im,vs,n,env=ns['smart_detect_and_annotate'](frame,conf_threshold=.5,frame_idx=1,**kw)
  row[key]=[{'label':v['label'],'confidence':v['confidence'],'bbox':v['bbox']} for v in vs]
  row[key+'_seconds']=round(time.perf_counter()-t,3)
 rows.append(row);print(json.dumps(row),flush=True)
for p in sorted(pathlib.Path(args.inputs).glob('test*')):
 if 'result' not in p.name:evaluate(cv2.imread(str(p)),p.name)
for p in sorted(pathlib.Path(args.inputs).glob('sample*.mp4')):
 cap=cv2.VideoCapture(str(p));total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT));
 for fraction in [0,.25,.5,.75]:
  idx=int((total-1)*fraction);cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,f=cap.read()
  if ok:
   h,w=f.shape[:2];scale=min(720/w,640/h,1);f=cv2.resize(f,(round(w*scale),round(h*scale)));evaluate(f,p.name+':'+str(idx))
 cap.release()
pathlib.Path('evaluation_v8.json').write_text(json.dumps(rows,indent=2))
