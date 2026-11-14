
from app.integrations.nonilion import send_reply
from app.integrations.gemini import generate_agent_reply

SUPPORTED_TYPES = {"console_message", "room_mention", "chat", "nearby", "test"}


async def handle_nonilion_event(event: dict):
    print(f"[LedgerLion] Handler started. Event: {event}", flush=True)

    try:
        event_type = event.get("type", "")

        if event_type == "test":
            print("[LedgerLion] Test event ignored.", flush=True)
            return

        if event_type not in SUPPORTED_TYPES:
            print(f"[LedgerLion] Unsupported event type: {event_type}", flush=True)
            return

        text = (event.get("text") or "").strip()
        api_base = event.get("api_base")
        message_id = event.get("message_id")

        if not api_base:
            raise ValueError("Nonilion event is missing api_base.")

        if not text:
            reply = (
                "I'm LedgerLion, your AI bookkeeping assistant. Send me a bill "
                "or ask a question about your business transactions."
            )
        else:
            try:
                print("[LedgerLion] Generating AI reply...", flush=True)
                reply = generate_agent_reply(
                    user_text=text,
                    event_context=event.get("instructions", "")
                )
                print("[LedgerLion] AI reply generated.", flush=True)
            except Exception as exc:
                print(
                    f"[LedgerLion] Gemini error: {type(exc).__name__}: {exc}",
                    flush=True
                )
                reply = (
                    "I received your message, but my AI service is temporarily "
                    "unavailable. Please try again shortly."
                )

        print("[LedgerLion] Sending reply to Nonilion...", flush=True)

        status = await send_reply(
            api_base=api_base,
            event_type=event_type,
            text=reply,
            message_id=message_id,
        )

        print(f"[LedgerLion] Reply sent. HTTP {status}", flush=True)

    except Exception as exc:
        print(
            f"[LedgerLion] Handler failed: {type(exc).__name__}: {exc}",
            flush=True
        )
        raise
