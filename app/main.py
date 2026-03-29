"""
main.py
-------
Punto de entrada de la aplicación FastAPI.
"""
import logging
from fastapi import FastAPI
from app.routers import webhook

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="WhatsApp Personal Assistant",
    description="Asistente personal powered by Claude AI",
    version="1.0.0",
)

# Registrar routers
app.include_router(webhook.router)


@app.get("/")
async def health_check():
    return {"status": "running", "message": "Asistente personal activo 🤖"}
