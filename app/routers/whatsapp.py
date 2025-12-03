from app.config import config
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import Response
from twilio.twiml.messaging_response import MessagingResponse
from twilio.request_validator import RequestValidator
from app.llm_service import llm_service
from app.utils.logger import logger

router = APIRouter(prefix="/webhook", tags=["whatsapp"])

validator = RequestValidator(config.TWILIO_AUTH_TOKEN)

async def handle_incoming_message(user_id: str, text: str) -> str:
    """
    Route WhatsApp messages into the existing LLM pipeline.
    """
    try:
        logger.info(f"[WhatsApp] Message from {user_id}: {text[:100]}...")
        reply = await llm_service.generate(text)
        logger.info(f"[WhatsApp] LLM reply length: {len(reply)}")
        return reply
    except Exception as e:
        logger.error(f"[WhatsApp] LLM generation failed: {e}")
        return "Sorry, I ran into an error while processing your message. Please try again later."

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request):
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)

    form = await request.form()
    post_data = dict(form)

    if not validator.validate(url, post_data, signature):
        raise HTTPException(status_code=403, detail="Invalid Twilio signature")
    
    wa_id = form.get("WaId")
    from_number = form.get("From")
    body = form.get("Body", "").strip()

    if not body:
        resp = MessagingResponse()
        resp.message("Empty message received.")
        return str(resp)
    
    user_id = wa_id or from_number or "unknown"

    ai_reply = await handle_incoming_message(user_id, body)

    resp = MessagingResponse()
    resp.message(ai_reply)

    return Response(content=str(resp), media_type="application/xml")