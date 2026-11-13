from app.agents import extractor, categorizer, auditor
from app.models import Transaction
from app.utils.ids import new_transaction_id, utc_now

def process_bill(image_bytes: bytes, mime_type: str, source_reference=None):
    data = extractor.run(image_bytes, mime_type)
    data = categorizer.run(data)
    data.update({
        "transaction_id": new_transaction_id(),
        "source_type": "image",
        "source_reference": source_reference,
        "created_at": utc_now(),
    })
    tx = Transaction(**data)
    return auditor.run(tx)
