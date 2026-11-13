from pathlib import Path
from datetime import date
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from app.config import settings

def _filter(rows, start, end):
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "transaction_date" in df:
        dates = pd.to_datetime(df["transaction_date"], errors="coerce")
        if start:
            df = df[dates >= pd.Timestamp(start)]
            dates = pd.to_datetime(df["transaction_date"], errors="coerce")
        if end:
            df = df[dates <= pd.Timestamp(end)]
    if "audit_status" in df:
        df = df[df["audit_status"] == "approved"]
    if not df.empty:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
    return df

def build_report(rows, start=None, end=None):
    df = _filter(rows, start, end)
    outdir = Path(settings.export_dir)
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = date.today().isoformat()
    xlsx = outdir / f"ledgerlion_report_{stamp}.xlsx"
    png = outdir / f"ledgerlion_chart_{stamp}.png"
    if df.empty:
        summary = {"transaction_count": 0, "income": 0, "expenses": 0, "net": 0, "by_category": {}}
    else:
        income = df[df["transaction_type"] == "income"]["amount"].sum()
        expenses = df[df["transaction_type"] == "expense"]["amount"].sum()
        by_cat = df[df["transaction_type"] == "expense"].groupby("category")["amount"].sum().to_dict()
        summary = {
            "transaction_count": int(len(df)), "income": round(float(income), 2),
            "expenses": round(float(expenses), 2), "net": round(float(income-expenses), 2),
            "by_category": {str(k): round(float(v), 2) for k,v in by_cat.items()}
        }
    with pd.ExcelWriter(xlsx, engine="openpyxl") as writer:
        (df if not df.empty else pd.DataFrame(columns=["No approved transactions"])).to_excel(
            writer, index=False, sheet_name="Transactions"
        )
        pd.DataFrame([{"metric": k, "value": v} for k,v in summary.items() if k != "by_category"]).to_excel(
            writer, index=False, sheet_name="Summary"
        )
        pd.DataFrame([{"category": k, "amount": v} for k,v in summary["by_category"].items()]).to_excel(
            writer, index=False, sheet_name="Categories"
        )
    cats = summary["by_category"]
    plt.figure(figsize=(9, 5))
    if cats:
        plt.bar(list(cats.keys()), list(cats.values()))
        plt.xticks(rotation=30, ha="right")
        plt.ylabel("Amount")
        plt.title("Expenses by category")
    else:
        plt.text(0.5, 0.5, "No approved expense data", ha="center", va="center")
        plt.axis("off")
    plt.tight_layout()
    plt.savefig(png, dpi=160)
    plt.close()
    summary.update({"excel_file": str(xlsx), "chart_file": str(png)})
    return summary
