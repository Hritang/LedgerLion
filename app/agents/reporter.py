from app.services.report_service import build_report
from app.integrations.sheets import read_transactions

def run(period_start=None, period_end=None):
    rows = read_transactions()
    return build_report(rows, period_start, period_end)
