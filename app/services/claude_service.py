"""
claude_service.py
-----------------
Cerebro del asistente: decide qué herramientas usar y genera la respuesta.
"""
import anthropic
from app.config import settings
from app.services import memory_service, gmail_service, calendar_service

client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

SYSTEM_PROMPT = """Eres un asistente personal inteligente accesible por WhatsApp.
Eres conciso, amigable y útil. Respondes en el mismo idioma que el usuario.

Tienes acceso a:
- Gmail del usuario (solo lectura)
- Google Calendar del usuario (lectura y creación de eventos)

Cuando el usuario pregunte por correos o eventos, usa la información que se te proporciona en el contexto.
Si el usuario quiere crear un evento, extrae: título, fecha/hora inicio, fecha/hora fin.
Usa formato ISO 8601 para fechas, zona horaria America/Bogota (UTC-5).

Comandos especiales que el usuario puede usar:
- /reset → limpiar historial de conversación
- /correos → ver últimos 5 correos
- /agenda → ver próximos 5 eventos
"""


def _detect_intent(message: str) -> dict:
    """Detecta si el usuario quiere correos, agenda, crear evento, etc."""
    msg = message.lower()
    return {
        "wants_emails": any(w in msg for w in ["/correos", "correo", "email", "inbox", "mail"]),
        "wants_calendar": any(w in msg for w in ["/agenda", "agenda", "calendario", "evento", "reunión", "cita"]),
        "wants_create_event": any(w in msg for w in ["crea", "agregar", "añadir", "programa", "agenda un"]),
        "wants_reset": "/reset" in msg,
    }


async def process_message(phone: str, user_message: str) -> str:
    """
    Procesa un mensaje del usuario y retorna la respuesta del asistente.
    """
    intent = _detect_intent(user_message)

    # Comando reset
    if intent["wants_reset"]:
        memory_service.clear_history(phone)
        return "🧹 Historial limpiado. ¡Empecemos de nuevo!"

    # Construir contexto extra si aplica
    extra_context = ""

    if intent["wants_emails"]:
        emails = gmail_service.get_recent_emails(max_results=5)
        extra_context += "\n\n" + gmail_service.format_emails_for_claude(emails)

    if intent["wants_calendar"]:
        events = calendar_service.get_upcoming_events(max_results=5)
        extra_context += "\n\n" + calendar_service.format_events_for_claude(events)

    # Recuperar historial
    history = memory_service.get_history(phone)

    # Construir mensaje con contexto
    full_user_message = user_message
    if extra_context:
        full_user_message = f"{user_message}\n\n[Contexto del sistema:{extra_context}]"

    # Guardar mensaje del usuario en historial
    memory_service.add_message(phone, "user", full_user_message)

    # Llamar a Claude
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=memory_service.get_history(phone),
    )

    assistant_reply = response.content[0].text

    # Si quiere crear un evento, intentamos parsear y crearlo
    if intent["wants_create_event"] and "dateTime" in assistant_reply:
        _try_create_event_from_reply(assistant_reply)

    # Guardar respuesta en historial
    memory_service.add_message(phone, "assistant", assistant_reply)

    return assistant_reply


def _try_create_event_from_reply(reply: str):
    """Intenta extraer y crear un evento si Claude respondió con datos de evento."""
    # Esta función es un hook para extensión futura con tool_use de Claude
    pass
