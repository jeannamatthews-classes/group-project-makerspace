import hashlib

def hash_uid(card_uid: str) -> str:
    """
    Hash the RFID card UID.
    """
    normalized_uid = card_uid.strip()
    return hashlib.sha256(normalized_uid.encode("utf-8")).hexdigest() # secure hashing technique 