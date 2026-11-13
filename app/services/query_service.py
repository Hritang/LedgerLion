from datetime import date
from app.integrations.sheets import read_transactions
from app.integrations.gemini import answer_from_computed_data

def answer_question(question: str, start=None, end=None):
    rows = read_transactions()
    approved = [r for r in rows if r.get("audit_status") == "approved"]
    if start:
        approved = [r for r in approved if (r.get("transaction_date") or "") >= start]
    if end:
        approved = [r for r in approved if (r.get("transaction_date") or "") <= end]
    income = sum(float(r.get("amount") or 0) for r in approved if r.get("transaction_type") == "income")
    expenses = sum(float(r.get("amount") or 0) for r in approved if r.get("transaction_type") == "expense")
    by_category = {}
    for r in approved:
        if r.get("transaction_type") == "expense":
            cat = r.get("category") or "Other / Needs Review"
            by_category[cat] = by_category.get(cat, 0) + float(r.get("amount") or 0)
    computed = {
        "transaction_count": len(approved), "income": round(income,2),
        "expenses": round(expenses,2), "net": round(income-expenses,2),
        "expenses_by_category": {k: round(v,2) for k,v in by_category.items()},
        "period_start": start, "period_end": end
    }
    explanation = answer_from_computed_data(question, computed)
    return {"computed": computed, "explanation": explanation}
