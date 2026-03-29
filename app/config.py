from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Anthropic
    anthropic_api_key: str

    # WhatsApp
    whatsapp_token: str
    whatsapp_phone_number_id: str
    whatsapp_verify_token: str

    # Google
    google_credentials_file: str = "credentials.json"
    google_token_file: str = "token.json"

    # App
    allowed_phone_number: str  # Solo este número puede usar el bot

    class Config:
        env_file = ".env"


settings = Settings()
