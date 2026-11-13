from app.models import Transaction
from app.services.transaction_service import save_if_valid

def run(tx: Transaction) -> dict:
    return save_if_valid(tx)
