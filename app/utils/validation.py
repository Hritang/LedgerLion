from datetime import date
from app.models import Transaction

REQUIRED_FOR_AUTO_SAVE = ("vendor", "transaction_date", "amount")
ALLOWED_CATEGORIES = {
    "Inventory / Stock", "Rent", "Salaries / Wages", "Utilities",
    "Transport / Delivery", "Marketing", "Equipment",
    "Repairs and Maintenance", "Office Supplies", "Other / Needs Review"
}

def audit_transaction(tx: Transaction) -> list[str]:
    flags = []
    if not tx.vendor:
        flags.append("Vendor is missing.")
    if not tx.transaction_date:
        flags.append("Transaction date is missing.")
    else:
        try:
            date.fromisoformat(tx.transaction_date[:10])
        except ValueError:
            flags.append("Transaction date is not in YYYY-MM-DD format.")
    if tx.amount <= 0:
        flags.append("Amount must be positive.")
    if tx.category not in ALLOWED_CATEGORIES:
        flags.append("Category is not in the configured category list.")
    if tx.tax_amount is not None and tx.tax_amount < 0:
        flags.append("Tax amount cannot be negative.")
    return flags
