"""
calendar_service.py
-------------------
Consulta y crea eventos en Google Calendar.
"""
from datetime import datetime, timezone
from typing import List, Dict
from googleapiclient.discovery import build

from app.services.gmail_service import _get_google_credentials


def get_upcoming_events(max_results: int = 5) -> List[Dict]:
    """Devuelve los próximos eventos del calendario principal."""
    creds = _get_google_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now(timezone.utc).isoformat()
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = events_result.get("items", [])
    formatted = []

    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        formatted.append({
            "title": event.get("summary", "Sin título"),
            "start": start,
            "location": event.get("location", ""),
            "description": event.get("description", ""),
        })

    return formatted


def create_event(title: str, start: str, end: str, description: str = "") -> Dict:
    """
    Crea un evento en el calendario.
    start / end deben estar en formato ISO 8601, ej: '2025-04-01T10:00:00-05:00'
    """
    creds = _get_google_credentials()
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start, "timeZone": "America/Bogota"},
        "end": {"dateTime": end, "timeZone": "America/Bogota"},
    }

    created = service.events().insert(calendarId="primary", body=event_body).execute()
    return {"id": created["id"], "link": created.get("htmlLink", "")}


def format_events_for_claude(events: List[Dict]) -> str:
    """Formatea eventos como texto para Claude."""
    if not events:
        return "No tienes eventos próximos."

    lines = ["📅 **Próximos eventos:**\n"]
    for i, event in enumerate(events, 1):
        loc = f"\n   📍 {event['location']}" if event["location"] else ""
        lines.append(f"{i}. **{event['title']}**\n   🕐 {event['start']}{loc}\n")

    return "\n".join(lines)
