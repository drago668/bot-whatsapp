"""
webhook.py
----------
Router de FastAPI que maneja los webhooks de WhatsApp.
- GET  /webhook  → verificación inicial de Meta
- POST /webhook  → mensajes entrantes
"""
import logging
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.services import claude_service, whatsapp_service

logger = logging.getLogger(__name__)
router = APIRouter()


# ── Verificación del webhook (Meta lo llama una sola vez al configurar) ──────
@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("Webhook verificado correctamente ✅")
        return PlainTextResponse(content=hub_challenge)
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


# ── Recepción de mensajes entrantes ──────────────────────────────────────────
@router.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()

    try:
        entry = body["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        # Ignorar notificaciones que no son mensajes (ej: status updates)
        if "messages" not in value:
            return {"status": "ok"}

        message = value["messages"][0]
        from_number = message["from"]

        # 🔒 Seguridad: solo tu número puede usar el bot
        if from_number != settings.allowed_phone_number.replace("+", ""):
            logger.warning(f"Número no autorizado intentó usar el bot: {from_number}")
            return {"status": "unauthorized"}

        # Solo procesamos mensajes de texto por ahora
        if message["type"] != "text":
            await whatsapp_service.send_text_message(
                from_number,
                "Por ahora solo puedo procesar mensajes de texto. 📝"
            )
            return {"status": "ok"}

        user_text = message["text"]["body"]
        logger.info(f"Mensaje recibido de {from_number}: {user_text[:50]}...")

        # Procesar con Claude y responder
        reply = await claude_service.process_message(from_number, user_text)
        await whatsapp_service.send_text_message(from_number, reply)

    except (KeyError, IndexError) as e:
        logger.error(f"Error parseando webhook payload: {e}")

    return {"status": "ok"}
