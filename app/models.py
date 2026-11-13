from pydantic import BaseModel, Field
from typing import Optional, Literal

class Transaction(BaseModel):
    transaction_id: str
    transaction_date: Optional[str] = None
    vendor: Optional[str] = None
    description: Optional[str] = None
    amount: float = Field(gt=0)
    currency: str = "INR"
    tax_amount: Optional[float] = None
    transaction_type: Literal["expense", "income"] = "expense"
    category: str = "Other / Needs Review"
    source_type: str = "image"
    source_reference: Optional[str] = None
    audit_status: str = "pending"
    audit_notes: str = ""
    created_at: str

class ClarificationRequest(BaseModel):
    transaction_id: str
    field: str
    value: str

class QuestionRequest(BaseModel):
    question: str
    period_start: Optional[str] = None
    period_end: Optional[str] = None

class ReportRequest(BaseModel):
    period_start: Optional[str] = None
    period_end: Optional[str] = None
    title: str = "LedgerLion Financial Report"
