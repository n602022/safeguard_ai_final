"""Application clock: all user-facing times are Vietnam time (UTC+7)."""
from datetime import datetime, timezone, timedelta

APP_TIMEZONE = timezone(timedelta(hours=7), name='Asia/Ho_Chi_Minh')

def app_now():
    return datetime.now(APP_TIMEZONE)

def app_today():
    return app_now().date()

def localize_timestamp(value):
    """Convert offset-aware input; legacy naive timestamps retain their wall time.

    A naive historic database value has no reliable source timezone. Do not
    silently shift it or shift already-correct local timestamps twice.
    """
    text = str(value or '').strip()
    try:
        stamp = datetime.fromisoformat(text.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return None
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=APP_TIMEZONE)
    return stamp.astimezone(APP_TIMEZONE)

def normalize_timestamp(value):
    stamp = localize_timestamp(value)
    return stamp.strftime('%Y-%m-%d %H:%M:%S') if stamp else str(value or '')

def format_timestamp_vn(value):
    stamp = localize_timestamp(value)
    return stamp.strftime('%d/%m/%Y %H:%M:%S') if stamp else str(value or '')
