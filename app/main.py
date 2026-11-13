from pathlib import Path
import hmac
from fastapi import FastAPI, UploadFile, File, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from app.config import settings
from app.agents.orchestrator import process_bill
from app.agents.message_handler import handle_nonilion_event
from app.models import QuestionRequest, ReportRequest
from app.services.query_service import answer_question
from app.agents.reporter import run as make_report

app = FastAPI(title="LedgerLion", version="1.1.0",
              description="AI bookkeeping backend for the Nonilion Island agent.")

@app.get("/health")
def health():
    return {"status": "ok", "service": "LedgerLion"}

@app.post("/api/bills")
async def upload_bill(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(415, "Upload JPG, PNG or WebP.")
    data = await file.read()
    if not data:
        raise HTTPException(400, "Empty upload.")
    if len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, f"File exceeds {settings.max_upload_mb} MB.")
    try:
        return process_bill(data, file.content_type, file.filename)
    except Exception as exc:
        raise HTTPException(502, f"Bill processing failed: {exc}")

@app.post("/api/questions")
def question(req: QuestionRequest):
    try:
        return answer_question(req.question, req.period_start, req.period_end)
    except Exception as exc:
        raise HTTPException(502, f"Question processing failed: {exc}")

@app.post("/api/reports")
def report(req: ReportRequest):
    try:
        result = make_report(req.period_start, req.period_end)
        return {
            "summary": {k:v for k,v in result.items() if k not in ("excel_file","chart_file")},
            "excel_url": "/api/files/" + Path(result["excel_file"]).name,
            "chart_url": "/api/files/" + Path(result["chart_file"]).name
        }
    except Exception as exc:
        raise HTTPException(502, f"Report generation failed: {exc}")

@app.get("/api/files/{filename}")
def download_file(filename: str):
    base = Path(settings.export_dir).resolve()
    path = (base / filename).resolve()
    if base not in path.parents or not path.is_file():
        raise HTTPException(404, "File not found.")
    return FileResponse(path, filename=path.name)

@app.post("/webhook")
async def nonilion_webhook(request: Request, background_tasks: BackgroundTasks):
    # The Nonilion dashboard sends Authorization: Bearer <WEBHOOK_SECRET>.
    expected = settings.webhook_secret
    supplied = request.headers.get("authorization", "")
    if not expected or not hmac.compare_digest(supplied, f"Bearer {expected}"):
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        event = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON event")

    if not isinstance(event, dict):
        raise HTTPException(status_code=400, detail="Event must be a JSON object")

    # Acknowledge immediately; Nonilion waits only five seconds.
    background_tasks.add_task(handle_nonilion_event, event)
    return {"ok": True}
