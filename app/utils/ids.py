import uuid
from datetime import datetime, timezone

def new_transaction_id() -> str:
    return "txn_" + uuid.uuid4().hex[:16]

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
