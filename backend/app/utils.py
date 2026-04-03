import hashlib
from datetime import datetime, timezone


def normalize_uid(card_uid: str) -> str:
    if card_uid is None:
        return ""

    normalized = str(card_uid).strip().upper()
    normalized = normalized.replace(" ", "")
    return normalized


def hash_uid(card_uid: str) -> str:
    normalized_uid = normalize_uid(card_uid)
    return hashlib.sha256(normalized_uid.encode("utf-8")).hexdigest()


def parse_iso_timestamp(value: str):
    if value is None or str(value).strip() == "":
        return datetime.now(timezone.utc)

    text = str(value).strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(text)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed.astimezone(timezone.utc)
