from datetime import datetime, timezone
from uuid import uuid4


def current_iso_datetime() -> str:
    return datetime.now(timezone.utc).isoformat()


def uuid() -> str:
    return uuid4().hex


def empty_dict() -> dict:
    return {}
