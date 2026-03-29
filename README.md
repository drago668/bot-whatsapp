# 🤖 WhatsApp Personal Assistant — powered by Claude AI

Asistente personal accesible desde WhatsApp, construido con FastAPI + Anthropic API + Google APIs.

---

## 🗂️ Estructura del proyecto

```
whatsapp-assistant/
├── app/
│   ├── main.py                  # Punto de entrada FastAPI
│   ├── config.py                # Variables de entorno (pydantic-settings)
│   ├── routers/
│   │   └── webhook.py           # Endpoints GET y POST /webhook
│   └── services/
│       ├── claude_service.py    # Lógica principal del asistente (Claude)
│       ├── whatsapp_service.py  # Envío de mensajes por WhatsApp API
│       ├── gmail_service.py     # Lectura de correos (Gmail API)
│       ├── calendar_service.py  # Lectura y creación de eventos (Google Calendar)
│       └── memory_service.py    # Historial de conversación en memoria
├── requirements.txt
├── Procfile                     # Para despliegue en Render
├── .env.example                 # Plantilla de variables de entorno
└── README.md
```

---

## ⚙️ Configuración paso a paso

### 1. Clonar y crear entorno virtual

```bash
git clone <tu-repo>
cd whatsapp-assistant
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
pip install -r requirements.txt
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Edita .env con tus credenciales reales
```

### 3. Obtener API Key de Anthropic

1. Ve a https://console.anthropic.com
2. Crea una cuenta y agrega créditos ($5 iniciales gratis)
3. En **API Keys** → crea una nueva key
4. Cópiala en `.env` como `ANTHROPIC_API_KEY`

### 4. Configurar WhatsApp Business API (Meta)

1. Ve a https://developers.facebook.com
2. Crea una nueva App → tipo **Business**
3. Agrega el producto **WhatsApp**
4. En **WhatsApp > Configuración de la API**:
   - Copia el **Token de acceso temporal** → `WHATSAPP_TOKEN`
   - Copia el **Phone Number ID** → `WHATSAPP_PHONE_NUMBER_ID`
5. El `WHATSAPP_VERIFY_TOKEN` es un string que **tú eliges** (ej: `mi_token_secreto_123`)

### 5. configuracion de credenciales de Google(OAuth 2.0)

#### 1. Crear proyecto en Google Cloud

1. Ve a [https://console.cloud.google.com](https://console.cloud.google.com)
2. Haz clic en el selector de proyecto (parte superior)
3. Selecciona **Nuevo proyecto**
4. Asigna un nombre al proyecto
5. Haz clic en **Crear**

---

#### 2. Activar APIs necesarias

Ir al menú:

APIs y servicios → Biblioteca

Buscar y activar las siguientes APIs:

* Gmail API
* Google Calendar API

También puedes acceder directamente:

* [https://console.cloud.google.com/apis/library/gmail.googleapis.com](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
* [https://console.cloud.google.com/apis/library/calendar-json.googleapis.com](https://console.cloud.google.com/apis/library/calendar-json.googleapis.com)

Haz clic en **Habilitar** en cada una.

---

#### 3. Configurar pantalla de consentimiento OAuth

Ir a:

[https://console.cloud.google.com/apis/credentials/consent](https://console.cloud.google.com/apis/credentials/consent)

Completar los campos:

* Nombre de la aplicación
* Correo electrónico de soporte al usuario

Tipo de usuario:

* Seleccionar **Externo**

Guardar los cambios.

---

#### 4. Agregar usuarios de prueba

En la misma pantalla de consentimiento OAuth o ingresa a este link [agregar usuarios de prueba](https://console.cloud.google.com/apis/credentials/consent) :

1. Buscar la sección **Usuarios de prueba (Test users)**
2. Hacer clic en **Agregar usuarios **
3. Agregar los correos Gmail que podrán usar la app mientras esté en modo testing
4. Guardar cambios

Ejemplo:

[usuario@gmail.com](mailto:usuario@gmail.com)
[equipo@gmail.com](mailto:equipo@gmail.com)

Solo los usuarios agregados podrán autenticarse mientras la app no esté verificada.

---

## 5. Crear credenciales OAuth 2.0

Ir a:

[https://console.cloud.google.com/apis/credentials](https://console.cloud.google.com/apis/credentials)

1. Clic en **Crear credenciales**
2. Seleccionar **ID de cliente de OAuth**
3. Tipo de aplicación:
   * Desktop App
4. Asignar nombre a la credencial
5. Crear

Descargar el archivo JSON.

Renombrar el archivo descargado a:

credentials.json

Colocar el archivo en la raíz del proyecto. [agregar usuarios de prueba](https://console.cloud.google.com/apis/credentials/consent) Esto genera `token.json` automáticamente

### 6. Correr localmente

```bash
uvicorn app.main:app --reload --port 8000
```

Para exponer tu localhost a internet (necesario para el webhook de Meta), usa [ngrok](https://ngrok.com):

```bash
ngrok http 8000
# Copia la URL https://xxxx.ngrok.io
```

### 7. Configurar el Webhook en Meta

1. En Meta Developers → WhatsApp → Configuración
2. En **Webhook URL**: `https://xxxx.ngrok.io/webhook`
3. En **Verify Token**: el valor que pusiste en `WHATSAPP_VERIFY_TOKEN`
4. Haz clic en **Verificar y guardar**
5. Suscríbete al campo `messages`

### 8. Desplegar en Render

1. Sube el proyecto a GitHub
2. Ve a https://render.com → New Web Service
3. Conecta tu repositorio
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Agrega las variables de entorno en el panel de Render
7. Copia la URL de Render (`https://tu-app.onrender.com`) y úsala como Webhook URL en Meta

---

## 💬 Comandos del asistente

| Comando           | Descripción                               |
| ----------------- | ------------------------------------------ |
| `/correos`      | Ver los últimos 5 correos del inbox       |
| `/agenda`       | Ver los próximos 5 eventos del calendario |
| `/reset`        | Limpiar el historial de conversación      |
| Cualquier mensaje | Conversar con el asistente                 |

---

## 💰 Costo estimado mensual

| Servicio                     | Costo                                 |
| ---------------------------- | ------------------------------------- |
| Anthropic API (Claude Haiku) | ~$1–2/mes uso personal               |
| WhatsApp Business API        | Gratis hasta 1,000 conversaciones/mes |
| Render (Free tier)           | Gratis                                |
| Google APIs                  | Gratis (cuotas generosas)             |
| **Total**              | **~$1–2/mes**                  |

---

## 🔒 Seguridad

- El bot solo responde al número definido en `ALLOWED_PHONE_NUMBER`
- Las API keys nunca se suben al repositorio (están en `.env` que está en `.gitignore`)
- Asegúrate de agregar `.env` y `token.json` a tu `.gitignore`

```gitignore
.env
token.json
credentials.json
__pycache__/
venv/
```
