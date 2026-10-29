"""Run once with Streamlit stopped: python repair_pending_status.py.
Only repairs AI-created pending decisions from the previous routing policy.
Never deletes/merges records or overrides human decisions.
"""
import json
import math
import sqlite3
from pathlib import Path
from datetime import datetime, timezone


def repair(db_path, evidence_dir):
    db_path, evidence_dir = Path(db_path), Path(evidence_dir)
    if not db_path.is_file():
        raise FileNotFoundError(db_path)
    eligible = []
    with sqlite3.connect(db_path) as db:
        for (eid,) in db.execute("SELECT event_id FROM events WHERE status='pending'"):
            path = evidence_dir / f'event_{eid}.json'
            try:
                meta = json.loads(path.read_text(encoding='utf-8'))
                score = float(meta['confidence'])
            except (OSError, ValueError, KeyError, TypeError):
                continue
            if (meta.get('status_origin') != 'ai_pending'
                    or meta.get('triage_rule') != 'verified_confidence_or_review_reason_v9'
                    or meta.get('confidence_kind', 'violation_score') != 'violation_score'
                    or not math.isfinite(score) or not .75 <= score <= 1):
                continue
            eligible.append((eid, path, meta))
        if not eligible:
            return [], None
        backup = db_path.parent / ('routing_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        backup.mkdir()
        with sqlite3.connect(backup / db_path.name) as dest:
            db.backup(dest)
        for eid, path, meta in eligible:
            (backup / path.name).write_bytes(path.read_bytes())
        for eid, path, meta in eligible:
            meta.update(current_status='confirmed', status_origin='ai_auto', auto_triaged=True,
                        triage_rule='confidence_threshold_v13', auto_confirm_threshold=.75,
                        verification_reason='threshold_pass')
            meta.setdefault('decision_history', []).append({
                'origin':'ai_auto','reason':'repair_legacy_threshold_routing',
                'timestamp':datetime.now(timezone.utc).isoformat(),
                'previous_status':'pending','new_status':'confirmed','confidence':meta['confidence']})
            temp = path.with_suffix('.json.tmp')
            temp.write_text(json.dumps(meta, ensure_ascii=False), encoding='utf-8')
            temp.replace(path)
            db.execute("UPDATE events SET status='confirmed' WHERE event_id=? AND status='pending'",(eid,))
    return [eid for eid, _, _ in eligible], backup


if __name__ == '__main__':
    from database import DB_PATH
    ids, backup = repair(DB_PATH, Path(__file__).resolve().parent/'evidence')
    print('Đã chuyển sang Đã xác nhận:', ids)
    print('Bản sao lưu:', backup or 'Không có hồ sơ đủ điều kiện cần sửa.')
