from datetime import datetime, timezone


def get_current_time() -> str:
    return datetime.now(timezone.utc).isoformat()
