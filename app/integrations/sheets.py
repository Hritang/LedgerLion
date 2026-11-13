from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.config import settings

HEADERS = [
    "transaction_id", "transaction_date", "vendor", "description", "amount",
    "currency", "tax_amount", "transaction_type", "category", "source_type",
    "source_reference", "audit_status", "audit_notes", "created_at"
]
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _service():
    if not settings.google_sheet_id:
        raise RuntimeError("GOOGLE_SHEET_ID is not configured.")
    creds = Credentials.from_service_account_file(
        settings.google_service_account_file, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=creds, cache_discovery=False)

def ensure_headers():
    svc = _service()
    current = svc.spreadsheets().values().get(
        spreadsheetId=settings.google_sheet_id, range="Transactions!A1:N1"
    ).execute().get("values", [])
    if not current:
        svc.spreadsheets().values().update(
            spreadsheetId=settings.google_sheet_id, range="Transactions!A1:N1",
            valueInputOption="RAW", body={"values": [HEADERS]}
        ).execute()

def read_transactions():
    ensure_headers()
    rows = _service().spreadsheets().values().get(
        spreadsheetId=settings.google_sheet_id, range="Transactions!A2:N"
    ).execute().get("values", [])
    return [dict(zip(HEADERS, row + [""] * (len(HEADERS)-len(row)))) for row in rows]

def append_transaction(tx: dict):
    ensure_headers()
    values = [[tx.get(h, "") if tx.get(h) is not None else "" for h in HEADERS]]
    return _service().spreadsheets().values().append(
        spreadsheetId=settings.google_sheet_id, range="Transactions!A:N",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": values}
    ).execute()

def append_audit_event(values: list):
    svc = _service()
    svc.spreadsheets().values().append(
        spreadsheetId=settings.google_sheet_id, range="Audit_Log!A:E",
        valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS",
        body={"values": [values]}
    ).execute()
