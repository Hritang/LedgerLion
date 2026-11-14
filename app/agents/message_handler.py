
import asyncio

from app.integrations.nonilion import send_reply
from app.integrations.gemini import generate_agent_reply


SUPPORTED_TYPES = {
    "console_message",
    "room_mention",
    "chat",
    "nearby",
    "test",
}

AI_TIMEOUT_SECONDS = 8


def get_instant_reply(user_text: str):
    """Handle common demo interactions without depending on Gemini."""

    message = user_text.lower().strip()

    greetings = {"hi", "hello", "hey", "hii", "helo", "good morning"}

    if message in greetings:
        return (
            "Hello! I'm LedgerLion, your AI bookkeeping assistant. "
            "I help small businesses organize bills, track expenses, "
            "categorize transactions and understand their finances. "
            "Try asking me for help or send a bill."
        )

    if message in {"help", "/help", "what can you do?"}:
        return (
            "Here's what I can help you with:\n"
            "1. Extract transaction details from bills.\n"
            "2. Categorize business expenses.\n"
            "3. Maintain a bookkeeping ledger.\n"
            "4. Summarize income and expenses.\n"
            "5. Generate financial reports.\n\n"
            "Send a bill or ask a bookkeeping question to get started."
        )

    if message in {"demo", "show demo", "start demo"}:
        return (
            "Welcome to the LedgerLion demo!\n\n"
            "Our workflow:\n"
            "1. Upload a bill or receipt.\n"
            "2. Extract vendor, date and amount.\n"
            "3. Categorize and audit the transaction.\n"
            "4. Store the approved transaction in the ledger.\n"
            "5. Generate financial summaries and reports.\n\n"
            "Let's get started!"
        )

    return None


def get_fallback_reply():
    return (
        "I'm LedgerLion. My AI service is temporarily experiencing "
        "high demand. The bookkeeping interface is available, but "
        "I couldn't process that question right now. "
        "Please try again shortly."
    )


async def handle_nonilion_event(event: dict):
    print("[LedgerLion] Handler started.", flush=True)

    try:
        event_type = event.get("type", "")

        if event_type == "test":
            return

        if event_type not in SUPPORTED_TYPES:
            print(
                f"[LedgerLion] Unsupported event: {event_type}",
                flush=True
            )
            return

        text = (event.get("text") or "").strip()
        api_base = event.get("api_base")
        message_id = event.get("message_id")

        if not api_base:
            raise ValueError("Nonilion event is missing api_base.")

        # Handle common interactions instantly.
        reply = get_instant_reply(text) if text else None

        if reply:
            print("[LedgerLion] Using instant response.", flush=True)

        elif not text:
            reply = (
                "I'm LedgerLion, your AI bookkeeping assistant. "
                "Send me a bill or ask a question about your transactions."
            )

        else:
            try:
                print("[LedgerLion] Generating AI reply...", flush=True)

                reply = await asyncio.wait_for(
                    generate_agent_reply(
                        user_text=text,
                        event_context=event.get("instructions", "")
                    ),
                    timeout=AI_TIMEOUT_SECONDS
                )

                print("[LedgerLion] AI reply generated.", flush=True)

            except Exception as exc:
                print(
                    f"[LedgerLion] AI unavailable: "
                    f"{type(exc).__name__}",
                    flush=True
                )
                reply = get_fallback_reply()

        print("[LedgerLion] Sending reply to Nonilion...", flush=True)

        status = await send_reply(
            api_base=api_base,
            event_type=event_type,
            text=reply,
            message_id=message_id,
        )

        print(
            f"[LedgerLion] Reply sent. HTTP {status}",
            flush=True
        )

    except Exception as exc:
        print(
            f"[LedgerLion] Handler failed: "
            f"{type(exc).__name__}: {exc}",
            flush=True
        )
        raise
