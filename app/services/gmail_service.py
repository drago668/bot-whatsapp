"""
gmail_service.py
----------------
Lee los últimos correos del inbox usando la Gmail API.
"""
import os
import base64
from typing import List, Dict
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/calendar.readonly",
]


def _get_google_credentials() -> Credentials:
    """Obtiene o refresca las credenciales de Google."""
    creds = None

    if os.path.exists(settings.google_token_file):
        creds = Credentials.from_authorized_user_file(settings.google_token_file, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                settings.google_credentials_file, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open(settings.google_token_file, "w") as token:
            token.write(creds.to_json())

    return creds


def get_recent_emails(max_results: int = 5) -> List[Dict]:
    """
    Devuelve los últimos correos del inbox.
    Retorna: lista de dicts con {from, subject, snippet, date}
    """
    creds = _get_google_credentials()
    service = build("gmail", "v1", credentials=creds)

    results = service.users().messages().list(
        userId="me", labelIds=["INBOX"], maxResults=max_results
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        msg_data = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["From", "Subject", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg_data["payload"]["headers"]}
        emails.append({
            "from": headers.get("From", "Desconocido"),
            "subject": headers.get("Subject", "Sin asunto"),
            "date": headers.get("Date", ""),
            "snippet": msg_data.get("snippet", ""),
        })

    return emails


def format_emails_for_claude(emails: List[Dict]) -> str:
    """Formatea los correos como texto para enviar a Claude."""
    if not emails:
        return "No hay correos recientes en el inbox."

    lines = ["📧 **Últimos correos:**\n"]
    for i, email in enumerate(emails, 1):
        lines.append(
            f"{i}. **De:** {email['from']}\n"
            f"   **Asunto:** {email['subject']}\n"
            f"   **Fecha:** {email['date']}\n"
            f"   **Resumen:** {email['snippet']}\n"
        )
    return "\n".join(lines)
