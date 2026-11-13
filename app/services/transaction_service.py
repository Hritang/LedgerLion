from app.integrations import sheets
from app.models import Transaction
from app.utils.validation import audit_transaction

def possible_duplicate(tx: Transaction) -> bool:
    # Simple exact-match check. For production, use a persistent idempotency key
    # and stronger matching (vendor/date/amount/currency/source hash).
    for row in sheets.read_transactions():
        try:
            same_amount = round(float(row.get("amount") or 0), 2) == round(tx.amount, 2)
        except ValueError:
            same_amount = False
        if (same_amount and row.get("vendor", "").strip().lower() == (tx.vendor or "").strip().lower()
            and row.get("transaction_date", "") == (tx.transaction_date or "")):
            return True
    return False

def save_if_valid(tx: Transaction) -> dict:
    flags = audit_transaction(tx)
    if flags:
        tx.audit_status = "needs_clarification"
        tx.audit_notes = "; ".join(flags)
        return {"saved": False, "flags": flags, "transaction": tx.model_dump()}
    if possible_duplicate(tx):
        tx.audit_status = "duplicate_review"
        tx.audit_notes = "Possible duplicate: matching vendor, date and amount."
        return {"saved": False, "flags": [tx.audit_notes], "transaction": tx.model_dump()}
    tx.audit_status = "approved"
    sheets.append_transaction(tx.model_dump())
    return {"saved": True, "flags": [], "transaction": tx.model_dump()}
