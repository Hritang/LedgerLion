import httpx
from app.config import settings

def _headers():
    if not settings.nonilion_bot_token:
        raise RuntimeError("NONILION_BOT_TOKEN is not configured.")
    return {
        "Authorization": f"Bearer {settings.nonilion_bot_token}",
        "Content-Type": "application/json",
    }

# async def send_reply(api_base: str, event_type: str, text: str, message_id: str | None = None):
#     # The Nonilion guide specifies /inbox for private messages and /chat
#     # for room mentions/chat. api_base is supplied in the incoming event.
#     if event_type == "nearby":
#         endpoint = "say"
#         payload = {"text": text}
#     elif event_type == "console_message":
#         endpoint = "inbox"
#         payload = {"text": text}
#         if message_id:
#             payload["reply_to"] = message_id
#     elif event_type in {"room_mention", "chat"}:
#         endpoint = "chat"
#         payload = {"text": text}
#     else:
#         raise ValueError(f"Unsupported Nonilion event type: {event_type}")

#     url = f"{api_base.rstrip('/')}/{endpoint}"
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         response = await client.post(url, headers=_headers(), json=payload)
#         response.raise_for_status()
#         return response.status_code


async def send_reply(api_base: str, event_type: str, text: str, message_id: str | None = None):
    if event_type == "nearby":
        endpoint = "say"
        payload = {"text": text}
    elif event_type == "console_message":
        endpoint = "inbox"
        payload = {"text": text}
        if message_id:
            payload["reply_to"] = message_id
    elif event_type in {"room_mention", "chat"}:
        endpoint = "chat"
        payload = {"text": text}
    else:
        raise ValueError(f"Unsupported Nonilion event type: {event_type}")

    url = f"{api_base.rstrip('/')}/{endpoint}"

    print(f"[LedgerLion] Sending reply: event_type={event_type}, endpoint={endpoint}, message_id={message_id}")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=_headers(), json=payload)

        print(f"[LedgerLion] Nonilion response: status={response.status_code}, body={response.text[:1000]}")

        response.raise_for_status()
        return response.status_code


async def send_speech(api_base: str, text: str, image_url: str | None = None):
    payload = {"text": text}
    if image_url:
        payload["image_url"] = image_url
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(
            f"{api_base.rstrip('/')}/say", headers=_headers(), json=payload
        )
        response.raise_for_status()
        return response.status_code
