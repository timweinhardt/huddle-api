from datetime import datetime, timezone


def get_current_time() -> str:
    return datetime.now(timezone.utc).isoformat()


def serialize_time(dt: datetime) -> str:
    """
    Converts a datetime object to a UTC ISO 8601 string.
    """
    # Convert to UTC and format
    return dt.astimezone(timezone.utc).isoformat()
