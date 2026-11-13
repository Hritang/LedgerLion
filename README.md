# LedgerLion — Nonilion-connected backend

LedgerLion is intended to be used from inside Nonilion Island. Render hosts the FastAPI backend; Nonilion provides the in-room agent character and message interface.

## Nonilion connection implemented from the guide you provided

- Public webhook route: `POST /webhook`
- Incoming authorization: `Authorization: Bearer <WEBHOOK_SECRET>`
- The route validates the sender key and schedules message handling as a background task, returning HTTP 200 immediately.
- `type == "console_message"` replies to `event.api_base + "/inbox"` with `{ "text": "...", "reply_to": "message_id" }`.
- Room messages / mentions reply to `event.api_base + "/chat"` with `{ "text": "..." }`.
- Replies use `Authorization: Bearer <NONILION_BOT_TOKEN>`.
- `type == "test"` is ignored.
- `/say` helper is included for voice output if needed.

The webhook handler uses the event fields shown in your screenshot: `type`, `text`, `message_id`, `api_base`, `sender`, `room_slug`, `bot_name` and `instructions`. It supports:
- `console_message` -> `/inbox` with `reply_to`
- `room_mention` and `chat` -> `/chat`
- `nearby` -> `/say`
- `test` -> ignored

Text messages currently receive a Gemini-generated conversational response. This proves the wake-up -> webhook -> AI -> reply loop, but it does not yet execute bookkeeping transactions from Nonilion messages. The screenshot does not show an attachment field or file-download schema, so bill-image handling from Nonilion still needs the attachment-specific documentation. The local `/api/bills` endpoint can already be tested independently.

## Configure environment

Copy `.env.example` to `.env` locally. On Render set:
- `GEMINI_API_KEY`
- `GOOGLE_SHEET_ID`
- `NONILION_BOT_TOKEN` (copy the one-time `nmcp_...` token)
- `WEBHOOK_SECRET` (same sender key configured in Nonilion)
- `GOOGLE_SERVICE_ACCOUNT_FILE=/etc/secrets/service-account.json`

Store the service account JSON as a Render Secret File at `/etc/secrets/service-account.json`. Never commit secrets.

## Local setup (Windows PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Test health at `http://127.0.0.1:8000/health`.

## Render

Use:
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/health`
- Instance: always-on, as Nonilion waits only five seconds for webhook acknowledgement.

After deployment, set the Nonilion webhook URL to:
`https://YOUR-SERVICE.onrender.com/webhook`

In Nonilion:
1. Name: LedgerLion
2. Select your room and appearance.
3. Paste the webhook URL.
4. Generate sender key; save the same value as `WEBHOOK_SECRET` in Render.
5. Connect and get token; copy the one-time `nmcp_...` token into Render as `NONILION_BOT_TOKEN`.
6. Deploy/redeploy after setting environment variables.
7. Test a private message and a room @mention.

## Important current limitations

- Exact attachment payload/download handling is not implemented because it is not present in the guide excerpt supplied so far.
- `/api/bills` works as a separate local/API route; wire it to Nonilion attachments once the attachment schema is known.
- CSV import, persistent clarification conversations, per-business isolation and voice delivery orchestration remain future work.
- The `api_base` supplied by the event is used as documented. For production, validate it against trusted Nonilion API hosts to prevent server-side request forgery; add the documented host allowlist before public production use.
