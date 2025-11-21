# 🐦 Guía Completa: Configurar Twitter/X para WebIAScraperNews

**Fecha:** 20 de Noviembre de 2025
**Tiempo estimado:** 30-40 minutos
**Dificultad:** Media (más complejo que Bluesky)

---

## 📋 Resumen del Proceso

1. ✅ Crear cuenta de Twitter/X (5 minutos)
2. ✅ Aplicar a Developer Account (10 minutos)
3. ✅ Crear una App (5 minutos)
4. ✅ Generar API Keys y Tokens (5 minutos)
5. ✅ Configurar en el proyecto (5 minutos)
6. ✅ Probar publicación (5 minutos)

---

## 🚀 PASO 1: Crear Cuenta de Twitter/X

### 1.1 Ve a Twitter
**URL:** https://twitter.com/ (o https://x.com/)

### 1.2 Regístrate
Click en **"Sign up"** o **"Registrarse"**

### 1.3 Completa el Registro
- **Nombre:** Schaller & Ponce AI News
- **Email:** schaller.ponce@gmail.com (o crea uno específico)
- **Usuario sugerido:** @SchalleryPonceAI o @SchallerPonceAI
  - También puede ser: @AINewsEspanol, @SchallerPonceIA

**Importante:**
- Verifica tu email
- Completa el perfil básico (foto, bio)
- **NO uses el mismo email** si quieres mantener cuentas separadas

### 1.4 Configurar Perfil Inicial
Usa el texto de `CHANNEL_BIOS.md` sección Twitter:

**Bio (160 caracteres):**
```
🤖 IA + Ciencia de Datos en español
📰 Resúmenes automáticos
🔗 Crédito a fuentes
ℹ️ Fair Use educativo
```

**Foto de perfil:** Logo o imagen representativa
**Banner:** Opcional (texto: "Noticias de IA en Español")

---

## 🔑 PASO 2: Aplicar a Developer Account

### 2.1 Ir al Portal de Desarrolladores
**URL:** https://developer.x.com/

### 2.2 Click en "Sign up"
- Inicia sesión con tu cuenta de Twitter recién creada
- Acepta los Términos de Servicio

### 2.3 Seleccionar Tipo de Cuenta
**Opciones:**
- ✅ **Free Tier** (Recomendado para empezar)
  - 1,500 posts/mes
  - Read and Write access
  - Gratis

- ⚠️ **Basic** ($100/mes) - Solo si necesitas más
  - 3,000 posts/mes
  - Advanced features

**Selecciona:** FREE TIER

### 2.4 Completar el Formulario de Aplicación

**Primary use case:**
```
Automated news aggregation and sharing of AI/ML content
```

**Describe your app:**
```
I'm building an automated news bot that shares summaries of
Artificial Intelligence, Machine Learning, and Data Science
news in Spanish. The bot:

- Aggregates tech news from various sources
- Creates brief summaries using AI
- Translates to Spanish for Hispanic audience
- Posts automatically with full attribution to sources
- Includes direct links to original articles
- Educational and non-commercial purpose

This helps democratize access to AI news for Spanish speakers.
```

**¿Usarás Twitter data?**
- NO (solo publicarás, no analizarás datos)

**¿Vas a mostrar tweets a usuarios?**
- NO

**¿Tu app usará datos de gobierno o políticos?**
- NO

**Acepta términos** y **Submit application**

### 2.5 Esperar Aprobación
- **Tiempo:** Puede ser instantáneo o tomar 1-3 días
- **Email:** Recibirás confirmación en schaller.ponce@gmail.com
- **Mientras esperas:** Puedes preparar el resto

---

## 📱 PASO 3: Crear una App (Después de Aprobación)

### 3.1 Ir a Developer Portal
**URL:** https://developer.x.com/en/portal/dashboard

### 3.2 Crear Nueva App
- Click en **"+ Create App"** o **"+ Add App"**
- **App name:** `WebIAScraperNewsBot` o similar
- **Description:** (Usar la misma descripción del paso 2.4)

### 3.3 Configurar App Settings
**User authentication setup:**
- Click en "Set up"
- **App permissions:**
  - ✅ **Read and Write** (necesario para publicar)
  - ❌ Direct Messages (no necesario)

**Type of App:**
- ✅ **Automated App or bot**

**Callback URL:** (Dejar vacío por ahora)
**Website URL:** https://github.com (o tu sitio si tienes)

---

## 🔐 PASO 4: Generar API Keys y Tokens

### 4.1 API Key and Secret
En tu App, ve a la pestaña **"Keys and tokens"**

**Generar API Keys:**
- Click en **"Generate"** en la sección "Consumer Keys"
- **Copiar y guardar:**
  - API Key (Consumer Key)
  - API Key Secret (Consumer Secret)

⚠️ **MUY IMPORTANTE:** Solo se muestran una vez!

### 4.2 Access Token and Secret
En la misma página:

**Generar Access Tokens:**
- Click en **"Generate"** en "Access Token and Secret"
- Seleccionar permisos: **Read and Write**
- **Copiar y guardar:**
  - Access Token
  - Access Token Secret

### 4.3 Bearer Token (Opcional)
Si está disponible:
- Click en **"Generate"** en "Bearer Token"
- Copiar y guardar

### 4.4 Guardar Credenciales Temporalmente
Crea un archivo temporal (NO lo commites a git):

`twitter_credentials_TEMP.txt`:
```
API Key: [tu_api_key]
API Key Secret: [tu_api_secret]
Access Token: [tu_access_token]
Access Token Secret: [tu_access_token_secret]
Bearer Token: [tu_bearer_token] (opcional)
```

---

## ⚙️ PASO 5: Configurar en el Proyecto

### 5.1 Editar .env.social_publisher

```bash
cd ~/Projects/webiascrap_v0.0.0
nano .env.social_publisher
```

### 5.2 Añadir Credenciales de Twitter

Busca la sección de Twitter y completa:

```bash
# ============================================================================
# TWITTER/X CREDENTIALS
# ============================================================================
TWITTER_API_KEY=tu_api_key_aqui
TWITTER_API_SECRET=tu_api_secret_aqui
TWITTER_ACCESS_TOKEN=tu_access_token_aqui
TWITTER_ACCESS_TOKEN_SECRET=tu_access_token_secret_aqui
TWITTER_BEARER_TOKEN=tu_bearer_token_aqui  # Opcional
```

### 5.3 Habilitar Twitter en Plataformas

Actualizar la línea de plataformas habilitadas:

```bash
ENABLED_PLATFORMS=telegram,bluesky,twitter
```

Guardar y cerrar (Ctrl+O, Enter, Ctrl+X)

---

## 🧪 PASO 6: Probar Publicación

### 6.1 Reiniciar Social Publisher

```bash
cd ~/Projects/webiascrap_v0.0.0
docker-compose stop social_publisher
docker-compose rm -f social_publisher
docker-compose up -d social_publisher
```

### 6.2 Ver Logs

```bash
docker-compose logs -f social_publisher
```

**Buscar:**
```
✅ Twitter: Adaptador inicializado
✅ Plataformas configuradas: telegram, bluesky, twitter
```

### 6.3 Crear Noticia de Prueba

1. Ir a http://localhost:8000
2. Buscar noticias
3. Seleccionar una
4. Copiar a "A Publicar"
5. Procesar con Claude
6. Esperar ~60 segundos (polling automático)

### 6.4 Verificar en Twitter

Abre tu perfil de Twitter:
https://twitter.com/[tu_usuario]

Deberías ver la noticia publicada con:
- ✅ Resumen
- ✅ Fuente identificada
- ✅ Link al original
- ✅ Hashtags
- ✅ Disclaimer

---

## ⚠️ PROBLEMAS COMUNES

### Problema 1: "Aplicación Rechazada"
**Solución:**
- Revisa el email con el motivo
- Generalmente piden más detalles
- Responde con información adicional
- Reaplica si es necesario

### Problema 2: "Error 403 - Forbidden"
**Causas:**
- Permisos insuficientes
- Token incorrecto

**Solución:**
- Verificar que los tokens tienen permisos Read and Write
- Regenerar tokens si es necesario

### Problema 3: "Error 401 - Unauthorized"
**Causas:**
- Credenciales incorrectas
- Tokens expirados

**Solución:**
- Verificar que copiaste bien las credenciales
- No debe haber espacios extra
- Regenerar si es necesario

### Problema 4: "Rate Limit Exceeded"
**Causas:**
- Demasiadas publicaciones muy rápido
- Free tier: máximo 1,500/mes

**Solución:**
- Reducir `MAX_NEWS_PER_CYCLE` en `.env.social_publisher`
- Aumentar `POLL_INTERVAL_SECONDS`

---

## 📊 Límites del Free Tier

| Característica | Límite |
|----------------|--------|
| Posts por mes | 1,500 |
| Posts por día | ~50 |
| Caracteres por post | 280 (estándar) o 4,000 (con suscripción) |
| Rate limit | 15 requests / 15 min |

**Para tu caso:**
- ~3-5 noticias/día = ~150/mes
- Muy por debajo del límite ✅

---

## 🔒 Seguridad

### ⚠️ NUNCA Compartas:
- API Keys
- API Secrets
- Access Tokens
- Bearer Tokens

### ✅ Buenas Prácticas:
- Mantener `.env.social_publisher` en `.gitignore`
- Regenerar tokens si sospechas compromiso
- No incluir credenciales en screenshots
- Usar tokens específicos por app

---

## 🎨 Personalización Avanzada (Opcional)

### Formato de Posts en Twitter
Archivo: `social_publisher/adapters/twitter.py`

Ya está implementado con:
- Resumen (máx 280 caracteres)
- Fuente identificada
- Link al original
- Hashtags relevantes
- Disclaimer legal

### Ajustar Mensajes
Si quieres personalizar, puedes editar el método `format_content()` en `twitter.py`

---

## 📝 Checklist Final

Antes de ir a producción con Twitter:

- [ ] Cuenta de Twitter creada
- [ ] Developer Account aprobado
- [ ] App creada en Developer Portal
- [ ] API Keys generadas y guardadas
- [ ] Credenciales configuradas en `.env.social_publisher`
- [ ] Twitter habilitado en `ENABLED_PLATFORMS`
- [ ] Social Publisher reiniciado
- [ ] Logs muestran "Twitter: Adaptador inicializado"
- [ ] Primera publicación de prueba exitosa
- [ ] Bio de Twitter actualizada con disclaimer
- [ ] Archivo temporal `twitter_credentials_TEMP.txt` eliminado

---

## 🚀 Siguiente Paso: LinkedIn

Una vez Twitter esté funcionando, LinkedIn será el último:
- Ver `SETUP_SOCIAL_MEDIA.md` sección LinkedIn
- Más complejo (OAuth 2.0)
- Tiempo estimado: 40-60 minutos

---

## 💡 Tips Finales

1. **Paciencia con la aprobación:** Puede tomar 1-3 días
2. **Free tier es suficiente:** Para uso de noticias
3. **Monitorea límites:** No exceder 1,500/mes
4. **Backup de tokens:** Guárdalos en lugar seguro (no en git)
5. **Test primero:** Usa pocas noticias para probar

---

## 📞 ¿Necesitas Ayuda?

**Si tienes problemas:**
1. Revisa la sección "Problemas Comunes"
2. Verifica logs: `docker-compose logs social_publisher`
3. Consulta documentación oficial: https://developer.x.com/en/docs
4. Contacto proyecto: schaller.ponce@gmail.com

---

## 🔗 Enlaces Útiles

- **Twitter/X:** https://twitter.com/
- **Developer Portal:** https://developer.x.com/
- **Documentación API:** https://developer.x.com/en/docs/twitter-api
- **Términos de Servicio:** https://developer.x.com/en/developer-terms
- **Rate Limits:** https://developer.x.com/en/docs/twitter-api/rate-limits

---

**¡Buena suerte con Twitter/X!** 🐦🚀

Una vez configurado, tendrás 3 plataformas activas:
✅ Telegram
✅ Bluesky
✅ Twitter/X

---

**Última actualización:** 20 de Noviembre de 2025
