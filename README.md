# Xtream API Checker

Bot de Telegram para verificar cuentas IPTV basadas en **Xtream Codes**. Permite comprobar el estado de una o múltiples cuentas, detectar contenido en español/latino y soporta múltiples formatos de entrada.

## Características

- **Verificación individual** — Comprueba una cuenta Xtream (server, user, pass) o desde un enlace M3U.
- **Verificación por lotes (batch)** — Envía un archivo `.txt` o pega múltiples líneas para verificar hasta 100 cuentas de una sola vez.
- **Detección de contenido español/latino** — Para cuentas válidas, escanea canales en vivo, películas VOD y series en busca de contenido en español/latino.
- **Auto-detección de formato** — Reconoce automáticamente si el input es un enlace M3U (`get.php?username=...`) o un trio Xtream (`server:puerto usuario contraseña`).
- **Barra de progreso** — Durante las verificaciones por lotes muestra el progreso en tiempo real.

## Comandos

| Comando | Descripción |
|---|---|
| `/start` | Mensaje de bienvenida y formatos soportados |
| `/help` | Guía detallada de uso y límites |
| `/batch` | Instrucciones para verificación masiva |
| `/cancel` | Cancela una verificación por lotes en curso |

## Formatos de entrada soportados

```
server:puerto usuario contraseña
```
```
http://server:puerto/get.php?username=xxx&password=xxx
```

## Requisitos

- Python 3.10+
- Token de bot de Telegram (via [@BotFather](https://t.me/BotFather))

## Instalación

```bash
git clone https://github.com/ialmontedr0/xtream-api-checker
cd xtream-api-checker

python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

pip install -r requirements.txt
```

Crea un archivo `.env` en la raíz:

```env
BOT_TOKEN=tu_token_de_telegram
```

## Ejecución

```bash
python main.py
```

## Variables de entorno

| Variable | Requerida | Default | Descripción |
|---|---|---|---|
| `BOT_TOKEN` | Sí | — | Token del bot de Telegram |
| `DEBUG` | No | `True` | Modo debug |
| `MAX_BATCH_SIZE` | No | `100` | Máximo de cuentas por lote |
| `BATCH_DELAY` | No | `1.0` | Segundos de espera entre verificaciones |

## Estructura del proyecto

```
xtream-api-checker/
├── main.py                          # Punto de entrada
├── config/
│   ├── settings.py                  # Configuración (pydantic-settings)
│   └── logging.py                   # Configuración de logging
├── app/
│   ├── core/
│   │   ├── http_client.py           # Cliente HTTP async (httpx)
│   │   └── exceptions.py            # Excepciones personalizadas
│   ├── models/
│   │   ├── request_dto.py           # DTO de solicitud (server, user, pass)
│   │   └── xtream_dto.py            # DTO de respuesta Xtream
│   ├── services/
│   │   ├── batch_checker.py         # Verificador por lotes
│   │   └── xtream/
│   │       └── service.py           # Servicio principal Xtream
│   ├── telegram/
│   │   ├── routers.py               # Registro de routers
│   │   └── handlers/check/
│   │       └── handler.py           # Handlers de comandos/mensajes
│   └── utils/
│       ├── m3u_parser.py            # Parser de enlaces M3U
│       ├── validators.py            # Validación y detección de input
│       └── formatter.py             # Formateo de respuestas
└── requirements.txt
```

## Licencia

MIT
