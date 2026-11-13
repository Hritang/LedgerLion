from app.integrations.gemini import extract_bill

def run(image_bytes: bytes, mime_type: str) -> dict:
    return extract_bill(image_bytes, mime_type)
