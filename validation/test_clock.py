import sys,pathlib,ast
from datetime import datetime,timezone
from unittest.mock import patch
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]))
import app_clock as clock
assert clock.normalize_timestamp('2026-10-28T18:22:52+00:00')=='2026-10-29 01:22:52'
assert clock.format_timestamp_vn('2026-10-28T18:22:52Z')=='29/10/2026 01:22:52'
assert clock.normalize_timestamp('2026-10-29T01:22:52+07:00')=='2026-10-29 01:22:52'
assert clock.normalize_timestamp('2026-10-29 01:22:52')=='2026-10-29 01:22:52'
assert clock.normalize_timestamp('bad')=='bad'
assert clock.app_now().utcoffset().total_seconds()==25200
stamp=datetime(2026,10,28,18,22,52,tzinfo=timezone.utc).astimezone(clock.APP_TIMEZONE)
with patch.object(clock,'app_now',return_value=stamp):assert clock.app_today().isoformat()=='2026-10-29'
# App modules must use the shared clock rather than host-local dates/times.
root=pathlib.Path(__file__).resolve().parents[1]
for p in [root/'core_logic.py',*list((root/'ui_pages').glob('*.py'))]:
 tree=ast.parse(p.read_text())
 for node in ast.walk(tree):
  if isinstance(node,ast.Call):
   assert ast.unparse(node.func) not in {'datetime.datetime.now','datetime.datetime.utcnow','datetime.date.today'},p
print('PASS: UTC+7; UTC conversion; day rollover; no double shift; legacy naive preservation; shared clock in all app pages')
