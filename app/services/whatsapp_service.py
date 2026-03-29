"""
whatsapp_service.py
-------------------
Envía mensajes de vuelta al usuario vía WhatsApp Cloud API.
"""
import httpx
from app.config import settings

WHATSAPP_API_URL = (
    f"https://graph.facebook.com/v20.0/{settings.whatsapp_phone_number_id}/messages"
)

HEADERS = {
    "Authorization": f"Bearer {settings.whatsapp_token}",
    "Content-Type": "application/json",
}


async def send_text_message(to: str, text: str) -> None:
    """Envía un mensaje de texto a un número de WhatsApp."""
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(WHATSAPP_API_URL, json=payload, headers=HEADERS)
        response.raise_for_status()


async def send_typing_indicator(to: str) -> None:
    """Opcional: muestra el indicador de 'escribiendo...' antes de responder."""
    # WhatsApp Business API no soporta typing indicators directamente,
    # pero podemos marcar el mensaje como leído para mejor UX
    pass
