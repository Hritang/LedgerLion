from app.utils.validation import ALLOWED_CATEGORIES

def run(candidate: dict) -> dict:
    category = candidate.get("category")
    if category not in ALLOWED_CATEGORIES:
        candidate["category"] = "Other / Needs Review"
    return candidate
