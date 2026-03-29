"""
memory_service.py
-----------------
Guarda el historial de conversación en memoria (por sesión).
Para persistencia real entre reinicios, podrías usar Redis o una DB.
"""
from collections import deque
from typing import List, Dict

# Máximo de mensajes que recordamos por usuario (para no gastar tokens de más)
MAX_HISTORY = 20

# Estructura: { "phone_number": deque([{role, content}, ...]) }
_conversation_store: Dict[str, deque] = {}


def get_history(phone: str) -> List[Dict]:
    """Devuelve el historial de conversación de un usuario."""
    if phone not in _conversation_store:
        _conversation_store[phone] = deque(maxlen=MAX_HISTORY)
    return list(_conversation_store[phone])


def add_message(phone: str, role: str, content: str) -> None:
    """Agrega un mensaje al historial de un usuario."""
    if phone not in _conversation_store:
        _conversation_store[phone] = deque(maxlen=MAX_HISTORY)
    _conversation_store[phone].append({"role": role, "content": content})


def clear_history(phone: str) -> None:
    """Limpia el historial de un usuario (útil para comando /reset)."""
    if phone in _conversation_store:
        _conversation_store[phone].clear()
