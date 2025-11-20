# 📱 SocialPublisher - Microservicio de Publicación en Redes Sociales

Microservicio que automatiza la publicación de noticias de IA en múltiples plataformas de redes sociales.

## 🎯 Funcionalidades

- ✅ Publicación automatizada en 4 plataformas:
  - **LinkedIn** - Marketing profesional
  - **Twitter/X** - Comunidad tech
  - **Bluesky** - Plataforma emergente
  - **Telegram** - Canal personal
- ✅ Sistema de queue interno para gestión de publicaciones
- ✅ Retry logic con backoff exponencial
- ✅ Rate limiting por plataforma
- ✅ Tracking de publicaciones en base de datos
- ✅ Health checks y logging detallado

## 🏗️ Arquitectura

```
┌──────────────────┐         ┌───────────────────┐
│  WebIAScraper    │◄────────┤  PostgreSQL       │
│  (Flask App)     │         │  (Shared DB)      │
└────────┬─────────┘         └───────────────────┘
         │ REST API
         │ /api/news/to-publish
         ▼
┌────────────────────────────────────────────────┐
│        SocialPublisher                         │
│        (Python Microservice)                   │
│                                                 │
│  Adaptadores (Strategy Pattern):               │
│   ✅ LinkedInAdapter                           │
│   ✅ TwitterAdapter                            │
│   ✅ BlueskyAdapter                            │
│   ✅ TelegramAdapter                           │
│                                                 │
│  Features:                                      │
│   • Queue de publicaciones                     │
│   • Retry Logic                                │
│   • Rate Limiting                              │
│   • Health checks                              │
└─────────────────────────────────────────────────┘
```

## 📋 Prerrequisitos

### 1. Cuentas y Credenciales

Necesitas crear cuentas de desarrollador en cada plataforma que desees usar:

#### LinkedIn
1. Ir a [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Crear una aplicación
3. Obtener `Client ID` y `Client Secret`
4. Configurar productos: "Share on LinkedIn" + "Sign In with LinkedIn"
5. Generar Access Token mediante flujo OAuth 2.0
6. Obtener tu `Person URN` (urn:li:person:xxxxx)

#### Twitter/X
1. Ir a [X Developer Portal](https://developer.x.com/)
2. Crear un proyecto y aplicación
3. Configurar permisos de "Read and Write"
4. Generar API Keys y Access Tokens
5. Copiar: API Key, API Secret, Access Token, Access Token Secret, Bearer Token

#### Bluesky
1. Crear cuenta en [Bluesky](https://bsky.app/)
2. Ir a Settings > App Passwords
3. Generar nuevo App Password
4. Copiar tu handle (usuario.bsky.social) y el app password

#### Telegram
1. Hablar con [@BotFather](https://t.me/botfather) en Telegram
2. Crear bot con `/newbot`
3. Copiar el Bot Token
4. Crear un canal público o privado
5. Añadir el bot como administrador del canal
6. Copiar el Channel ID (para canales públicos: @nombre_canal)

## 🚀 Instalación y Configuración

### 1. Configurar Variables de Entorno

```bash
cd ~/Projects/webiascrap_v0.0.0

# Copiar archivo de ejemplo
cp .env.social_publisher.example .env.social_publisher

# Editar y completar con tus credenciales
nano .env.social_publisher
```

### 2. Configurar Credenciales

Edita `.env.social_publisher` y completa las credenciales de las plataformas que desees usar:

```bash
# LinkedIn
LINKEDIN_CLIENT_ID=tu_client_id
LINKEDIN_CLIENT_SECRET=tu_client_secret
LINKEDIN_ACCESS_TOKEN=tu_access_token
LINKEDIN_PERSON_URN=urn:li:person:ABC123

# Twitter/X
TWITTER_API_KEY=tu_api_key
TWITTER_API_SECRET=tu_api_secret
TWITTER_ACCESS_TOKEN=tu_access_token
TWITTER_ACCESS_TOKEN_SECRET=tu_access_token_secret
TWITTER_BEARER_TOKEN=tu_bearer_token

# Bluesky
BLUESKY_HANDLE=usuario.bsky.social
BLUESKY_APP_PASSWORD=tu_app_password

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdef...
TELEGRAM_CHANNEL_ID=@mi_canal
```

### 3. Habilitar Plataformas

En `.env.social_publisher`, configura qué plataformas quieres usar:

```bash
# Solo usar las que tengas configuradas
ENABLED_PLATFORMS=linkedin,twitter,bluesky,telegram

# O solo algunas:
ENABLED_PLATFORMS=twitter,telegram
```

### 4. Iniciar el Servicio

```bash
# Iniciar todo (WebIAScraper + SocialPublisher)
docker-compose up --build

# Solo SocialPublisher
docker-compose up social_publisher

# En modo daemon (background)
docker-compose up -d social_publisher
```

## 📊 Uso

### Flujo de Trabajo

1. **WebIAScraper** scrapea noticias de IA
2. Usuario selecciona noticias para publicar (añade a tabla `apublicar`)
3. Usuario procesa noticias (traducción + optimización para RRSS)
4. **SocialPublisher** (cada 5 minutos por defecto):
   - Consulta API de WebIAScraper para obtener noticias pendientes
   - Añade a queue interna
   - Publica en todas las plataformas habilitadas
   - Marca como publicadas en la BD

### Ver Logs

```bash
# Logs en tiempo real
docker-compose logs -f social_publisher

# Últimas 100 líneas
docker-compose logs --tail=100 social_publisher

# Logs dentro del container
docker exec -it webiascrap_social_publisher tail -f /app/logs/social_publisher.log
```

### Verificar Estado

```bash
# Ver si está corriendo
docker-compose ps social_publisher

# Health check
docker exec webiascrap_social_publisher pgrep -f 'python -m social_publisher.main'
```

### Detener el Servicio

```bash
# Detener solo SocialPublisher
docker-compose stop social_publisher

# Detener todo
docker-compose down
```

## 🔧 Configuración Avanzada

### Intervalos de Polling

Edita `.env.social_publisher`:

```bash
# Consultar cada 5 minutos (default)
POLL_INTERVAL_SECONDS=300

# Consultar cada hora
POLL_INTERVAL_SECONDS=3600

# Consultar cada 30 minutos
POLL_INTERVAL_SECONDS=1800
```

### Límites de Publicación

```bash
# Máximo de noticias a procesar por ciclo
MAX_NEWS_PER_CYCLE=5

# Reintentos en caso de error
MAX_RETRIES=3
RETRY_DELAY_SECONDS=60
```

## 📈 Monitoreo

### Estadísticas de Publicación

Las publicaciones se registran en la tabla `apublicar`:

```sql
-- Ver noticias publicadas
SELECT
    id,
    titulo_es,
    publicado,
    plataformas_publicadas,
    published_at
FROM apublicar
WHERE publicado = true;

-- Ver errores recientes
SELECT
    id,
    titulo_es,
    ultimo_error,
    intentos_publicacion
FROM apublicar
WHERE ultimo_error IS NOT NULL;
```

### Health Check

El servicio incluye health checks automáticos:

```bash
# Ver estado de health check
docker inspect webiascrap_social_publisher | grep -A 10 Health
```

## 🐛 Troubleshooting

### Error: "No hay adaptadores disponibles"

**Causa:** Ninguna plataforma tiene credenciales válidas.

**Solución:**
1. Verifica que `.env.social_publisher` existe y tiene credenciales
2. Verifica que las credenciales son correctas
3. Verifica logs: `docker-compose logs social_publisher`

### Error: "Autenticación fallida" para una plataforma

**LinkedIn:**
- Verifica que el Access Token no haya expirado (duran 60 días)
- Renueva el token mediante OAuth 2.0 flow

**Twitter:**
- Verifica que tienes permisos de "Read and Write"
- Verifica que el Bearer Token es correcto

**Bluesky:**
- Verifica que usaste un App Password (NO tu contraseña normal)
- Verifica que el handle incluye `.bsky.social`

**Telegram:**
- Verifica que el bot es administrador del canal
- Verifica que el Channel ID es correcto (@canal o -100xxx)

### Las noticias no se publican

**Verifica:**
1. Que las noticias están marcadas como `procesado = true` en la tabla `apublicar`
2. Que las noticias NO están marcadas como `publicado = true`
3. Que WebIAScraper está corriendo y accesible
4. Que SocialPublisher puede conectarse a la API de WebIAScraper

```bash
# Test manual de la API
curl http://localhost:8000/api/news/to-publish
```

## 📚 API de WebIAScraper

SocialPublisher usa estos endpoints:

### GET /api/news/to-publish

Obtener noticias pendientes de publicar.

**Query params:**
- `procesados` (bool): Solo noticias procesadas (default: true)
- `limit` (int): Máximo de noticias (default: 10)

**Response:**
```json
{
  "count": 2,
  "noticias": [
    {
      "id": 123,
      "titulo_es": "Nueva versión de GPT...",
      "resumen_corto": "OpenAI lanza GPT-5...",
      "url": "https://...",
      "hashtags": "#AI,#GPT5",
      "procesado": true,
      "publicado": false
    }
  ]
}
```

### POST /api/news/{id}/mark-published

Marcar noticia como publicada.

**Body:**
```json
{
  "platform": "linkedin",
  "post_id": "urn:li:share:123456",
  "post_url": "https://linkedin.com/...",
  "error": null
}
```

## 🔐 Seguridad

- ⚠️ **NUNCA** commitees `.env.social_publisher` al repositorio
- ⚠️ Usa `.env.social_publisher.example` como template
- ⚠️ Rota tus tokens periódicamente
- ⚠️ En producción, usa Docker Secrets o servicios de gestión de secretos

## 📖 Referencias

- [LinkedIn API Documentation](https://learn.microsoft.com/en-us/linkedin/)
- [Twitter/X API Documentation](https://developer.x.com/en/docs)
- [Bluesky AT Protocol](https://docs.bsky.app/)
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 🤝 Contribuciones

Desarrollado con Claude Code (Anthropic)

---

**Versión:** 0.1.0
**Fecha:** Noviembre 2025
