from datetime import datetime, timezone

def as_aware_utc(dt: datetime) -> datetime:
    """Ensure a datetime is timezone-aware (assumes UTC if naive).
    Needed because SQLite returns naive datetimes even for tz-aware columns.
    """
    return dt.replace(tzinfo=timezone.utc) if dt.tzinfo is None else dt
