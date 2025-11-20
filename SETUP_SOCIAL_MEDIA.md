# 🚀 Guía de Configuración: Automatización de Redes Sociales

Guía paso a paso para configurar la publicación automatizada en LinkedIn, Twitter, Bluesky y Telegram.

---

## 📋 Tabla de Contenidos

1. [Preparación](#1-preparación)
2. [LinkedIn](#2-linkedin)
3. [Twitter/X](#3-twitterx)
4. [Bluesky](#4-bluesky)
5. [Telegram](#5-telegram)
6. [Configuración Final](#6-configuración-final)
7. [Primer Despliegue](#7-primer-despliegue)

---

## 1. Preparación

### 1.1 Actualizar Base de Datos

Primero, necesitamos migrar la base de datos para añadir las columnas de tracking:

```bash
cd ~/Projects/webiascrap_v0.0.0

# Conectar a la base de datos (si ya está corriendo)
docker-compose exec db psql -U webiauser -d webiascrap -f /migrations/001_add_publication_tracking.sql

# O ejecutar manualmente:
docker-compose exec db psql -U webiauser -d webiascrap

# Dentro de psql, copiar y ejecutar el contenido de migrations/001_add_publication_tracking.sql
```

### 1.2 Crear Archivo de Configuración

```bash
# Copiar template
cp .env.social_publisher.example .env.social_publisher

# Abrir para editar
nano .env.social_publisher
```

---

## 2. LinkedIn

### 2.1 Crear Aplicación de LinkedIn

1. Ve a [LinkedIn Developer Portal](https://www.linkedin.com/developers/)
2. Click en "Create app"
3. Completa:
   - **App name:** WebIAScraper Social Publisher
   - **LinkedIn Page:** Usa tu perfil personal o crea una página
   - **App logo:** Opcional
   - **Privacy policy URL:** Opcional para desarrollo
   - **Terms of use URL:** Opcional para desarrollo

4. Click "Create app"

### 2.2 Configurar Productos

1. En tu app, ve a la pestaña **"Products"**
2. Añade estos productos:
   - ✅ **"Share on LinkedIn"**
   - ✅ **"Sign In with LinkedIn using OpenID Connect"**
3. Click "Add product" para cada uno

### 2.3 Obtener Credenciales

1. Ve a la pestaña **"Auth"**
2. Copia:
   - **Client ID**
   - **Client Secret**

### 2.4 Generar Access Token (OAuth 2.0)

LinkedIn requiere un flujo OAuth completo. Opciones:

**Opción A: Usar herramienta de LinkedIn (Recomendado para testing)**

1. Ve a la pestaña **"Auth"** de tu app
2. En **"OAuth 2.0 scopes"**, añade:
   - `openid`
   - `profile`
   - `w_member_social`
3. Click en "Generate token" (si está disponible)

**Opción B: Flujo OAuth manual**

```bash
# 1. Construir URL de autorización
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=TU_CLIENT_ID&redirect_uri=http://localhost:8000/callback&scope=openid%20profile%20w_member_social

# 2. Abrir en navegador, autorizar
# 3. Copiar el código de la URL de callback
# 4. Intercambiar código por access token:

curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=authorization_code' \
  -d 'code=TU_CODIGO_AQUI' \
  -d 'client_id=TU_CLIENT_ID' \
  -d 'client_secret=TU_CLIENT_SECRET' \
  -d 'redirect_uri=http://localhost:8000/callback'
```

### 2.5 Obtener Person URN

```bash
# Con tu access token:
curl -X GET https://api.linkedin.com/v2/me \
  -H 'Authorization: Bearer TU_ACCESS_TOKEN'

# La respuesta incluirá tu Person URN: "urn:li:person:ABC123XYZ"
```

### 2.6 Configurar en .env

```bash
LINKEDIN_CLIENT_ID=tu_client_id
LINKEDIN_CLIENT_SECRET=tu_client_secret
LINKEDIN_ACCESS_TOKEN=tu_access_token
LINKEDIN_PERSON_URN=urn:li:person:ABC123
```

---

## 3. Twitter/X

### 3.1 Crear Cuenta de Desarrollador

1. Ve a [X Developer Portal](https://developer.x.com/)
2. Sign up con tu cuenta de Twitter
3. Completa el formulario de aplicación
4. Espera aprobación (generalmente instantáneo para Free tier)

### 3.2 Crear Proyecto y App

1. Click en "Create Project"
2. Completa:
   - **Project name:** WebIAScraper
   - **Use case:** Making a bot
   - **Project description:** Automated AI news sharing

3. Click "Next" y luego "Create App"
4. **App name:** webiascrap_publisher (debe ser único)

### 3.3 Configurar Permisos

1. En tu app, ve a **"Settings"**
2. En **"User authentication settings"**, click "Set up"
3. Configura:
   - **App permissions:** Read and Write
   - **Type of App:** Web App
   - **Callback URL:** `http://localhost:8000/callback` (para desarrollo)
   - **Website URL:** `http://localhost:8000`

4. Click "Save"

### 3.4 Obtener Credenciales

1. Ve a **"Keys and tokens"**
2. Regenera (si es necesario) y copia:
   - ✅ **API Key**
   - ✅ **API Key Secret**
   - ✅ **Bearer Token**

3. En **"Access Token and Secret"**, click "Generate":
   - ✅ **Access Token**
   - ✅ **Access Token Secret**

### 3.5 Configurar en .env

```bash
TWITTER_API_KEY=tu_api_key
TWITTER_API_SECRET=tu_api_secret
TWITTER_ACCESS_TOKEN=tu_access_token
TWITTER_ACCESS_TOKEN_SECRET=tu_access_token_secret
TWITTER_BEARER_TOKEN=tu_bearer_token
```

---

## 4. Bluesky

### 4.1 Crear Cuenta

1. Descarga la app de [Bluesky](https://bsky.app/) (iOS/Android)
2. O regístrate en https://bsky.app/
3. Completa el registro

### 4.2 Generar App Password

1. En la app/web, ve a **Settings**
2. Ve a **Privacy and Security**
3. Click en **App Passwords**
4. Click **"Add App Password"**
5. Nombre: `WebIAScraper`
6. Click "Create"
7. ⚠️ **IMPORTANTE:** Copia el password INMEDIATAMENTE (no se mostrará de nuevo)

### 4.3 Configurar en .env

```bash
BLUESKY_HANDLE=tu_usuario.bsky.social  # Con el .bsky.social
BLUESKY_APP_PASSWORD=tu_app_password_generado
```

---

## 5. Telegram

### 5.1 Crear Bot

1. Abre Telegram
2. Busca [@BotFather](https://t.me/botfather)
3. Envía `/newbot`
4. Sigue las instrucciones:
   - **Bot name:** WebIAScraper News Bot (puede ser cualquier cosa)
   - **Bot username:** webiascrap_news_bot (debe terminar en _bot)

5. Copia el **Bot Token** (formato: `123456789:ABCdef...`)

### 5.2 Crear Canal

**Opción A: Canal Público**

1. En Telegram, click en el menú hamburguesa
2. Click en "New Channel"
3. Nombre: "WebIAScraper AI News" (o el que prefieras)
4. Descripción: Opcional
5. Selecciona **"Public channel"**
6. Username del canal: `@tu_canal_aqui`

**Opción B: Canal Privado**

1. Similar al público, pero selecciona "Private channel"
2. Necesitarás obtener el ID del canal (numérico)

### 5.3 Añadir Bot como Administrador

1. Abre tu canal
2. Click en el nombre del canal (arriba)
3. Click en **"Administrators"**
4. Click **"Add Administrator"**
5. Busca tu bot por username (@webiascrap_news_bot)
6. Dale permisos de:
   - ✅ Post messages
   - ✅ Edit messages (opcional)
   - ✅ Delete messages (opcional)

### 5.4 Obtener Channel ID

**Para canal público:**
```bash
# El ID es simplemente: @tu_canal
TELEGRAM_CHANNEL_ID=@webiascrap_news
```

**Para canal privado:**
```bash
# Necesitas obtener el ID numérico
# 1. Añade tu bot al canal como admin
# 2. Envía un mensaje al canal
# 3. Usa la API de Telegram:

curl https://api.telegram.org/bot<TU_BOT_TOKEN>/getUpdates

# Busca en la respuesta el campo "chat": { "id": -100123456789 }
# Ese es tu Channel ID
TELEGRAM_CHANNEL_ID=-100123456789
```

### 5.5 Configurar en .env

```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@webiascrap_news  # O -100123456789 para privados
```

---

## 6. Configuración Final

### 6.1 Revisar archivo .env.social_publisher

Tu archivo debe verse así (con tus credenciales reales):

```bash
# WebIAScraper API
WEBIASCRAPER_API_URL=http://app:8000

# Plataformas habilitadas
ENABLED_PLATFORMS=linkedin,twitter,bluesky,telegram

# Configuración
POLL_INTERVAL_SECONDS=300  # 5 minutos
MAX_NEWS_PER_CYCLE=5

# LinkedIn
LINKEDIN_CLIENT_ID=78abc...
LINKEDIN_CLIENT_SECRET=wxyz...
LINKEDIN_ACCESS_TOKEN=AQV...
LINKEDIN_PERSON_URN=urn:li:person:ABC123

# Twitter/X
TWITTER_API_KEY=dEfG...
TWITTER_API_SECRET=hIjK...
TWITTER_ACCESS_TOKEN=1234...
TWITTER_ACCESS_TOKEN_SECRET=lMnO...
TWITTER_BEARER_TOKEN=AAAA...

# Bluesky
BLUESKY_HANDLE=carlos.bsky.social
BLUESKY_APP_PASSWORD=abcd-efgh-ijkl-mnop

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHANNEL_ID=@webiascrap_news
```

### 6.2 Verificar Permisos

```bash
# El archivo .env.social_publisher NO debe estar en git
ls -la .env.social_publisher  # Debe existir
cat .gitignore | grep .env.social_publisher  # Debe estar ignorado
```

---

## 7. Primer Despliegue

### 7.1 Build y Deploy

```bash
cd ~/Projects/webiascrap_v0.0.0

# Build de ambos servicios
docker-compose build

# Iniciar todo
docker-compose up -d

# Ver logs de SocialPublisher
docker-compose logs -f social_publisher
```

### 7.2 Verificar que Todo Funciona

Deberías ver en los logs:

```
✅ LinkedIn: Adaptador inicializado
✅ Twitter: Adaptador inicializado
✅ Bluesky: Adaptador inicializado
✅ Telegram: Adaptador inicializado
🔄 Iniciando loop de polling...
```

### 7.3 Test Manual

1. **Crear noticia de prueba:**
   - Abre WebIAScraper: http://localhost:8000
   - Selecciona una noticia
   - Click en "Copiar a 'A Publicar'"
   - En la lista de "A Publicar", click en "Procesar" (traduce y optimiza)

2. **Esperar o forzar publicación:**
   - Espera 5 minutos (o el intervalo configurado)
   - O reinicia el servicio: `docker-compose restart social_publisher`

3. **Verificar publicación:**
   - Ve a tus redes sociales y verifica que se publicó
   - Revisa logs: `docker-compose logs social_publisher`
   - Verifica en BD que `publicado = true`

### 7.4 Verificar en Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec db psql -U webiauser -d webiascrap

# Ver noticias publicadas
SELECT id, titulo_es, publicado, plataformas_publicadas
FROM apublicar
WHERE publicado = true;

# Ver errores
SELECT id, titulo_es, ultimo_error
FROM apublicar
WHERE ultimo_error IS NOT NULL;
```

---

## 🎉 ¡Listo!

Tu sistema de publicación automatizada está funcionando. Ahora:

1. Las noticias que selecciones y proceses se publicarán automáticamente
2. Cada 5 minutos (o tu intervalo configurado)
3. En todas las plataformas habilitadas

## 📊 Próximos Pasos

- Ajusta el intervalo de polling según tus necesidades
- Monitorea los logs regularmente
- Rota tus tokens periódicamente (especialmente LinkedIn que expira cada 60 días)
- Personaliza los formatos de mensaje en cada adaptador si lo deseas

## ❓ Troubleshooting

Si algo falla, revisa:
1. Logs: `docker-compose logs -f social_publisher`
2. Credenciales en `.env.social_publisher`
3. Health checks: `docker-compose ps`
4. Conectividad: `docker-compose exec social_publisher ping app`

---

**Happy Publishing! 🚀**
