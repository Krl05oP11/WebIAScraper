# 💼 Guía Completa: Configurar LinkedIn para WebIAScraperNews

**Fecha:** 20 de Noviembre de 2025
**Tiempo estimado:** 60-90 minutos
**Dificultad:** Alta (la más compleja de todas las plataformas)

---

## 📋 Resumen del Proceso

1. ✅ Crear una LinkedIn Page (no personal profile) (10 minutos)
2. ✅ Crear una App en LinkedIn Developer (15 minutos)
3. ✅ Configurar OAuth 2.0 y obtener permisos (20 minutos)
4. ✅ Implementar OAuth 2.0 flow para obtener tokens (20 minutos)
5. ✅ Configurar en el proyecto (10 minutos)
6. ✅ Probar publicación (10 minutos)

---

## ⚠️ IMPORTANTE: LinkedIn Requiere una Company Page

**NO puedes publicar en un perfil personal vía API.**

LinkedIn API solo permite publicar en:
- ✅ **LinkedIn Company Pages** (páginas de empresa/organización)
- ❌ Personal Profiles (perfiles personales) - BLOQUEADO por API

Por lo tanto, el primer paso es crear una LinkedIn Page.

---

## 🏢 PASO 1: Crear LinkedIn Page

### 1.1 Requisitos
- Tener un perfil personal de LinkedIn activo
- El perfil debe tener tu nombre real y estar completo
- LinkedIn puede rechazar páginas de bots o cuentas sospechosas

### 1.2 Crear la Page

1. **Ir a:** https://www.linkedin.com/company/setup/new/
2. **Tipo de página:** Seleccionar **"Company"**
3. **Información de la página:**
   - **Page name:** `Schaller & Ponce AI News`
   - **LinkedIn public URL:** `schaller-ponce-ai-news` (o similar disponible)
   - **Website:** `https://github.com/[tu-usuario]/webiascrap` (o tu sitio)
   - **Industry:** `Technology, Information and Internet`
   - **Company size:** `1-10 employees` o `Self-employed`
   - **Company type:** `Educational` o `Self-Owned`
   - **Logo:** Sube un logo/imagen representativa

4. **Descripción de la página:**
```
🤖 Noticias de Inteligencia Artificial y Ciencia de Datos en español

Resúmenes automáticos de las últimas noticias sobre IA, Machine Learning,
Deep Learning y Data Science, traducidos al español para la comunidad
hispanohablante.

📰 Todo el contenido incluye atribución completa a las fuentes originales
🔗 Links directos a artículos completos
ℹ️ Resúmenes generados automáticamente - Fair Use educativo

Contacto: schaller.ponce@gmail.com
```

5. **Marcar:**
   - ✅ "I verify that I am authorized to act on behalf of this organization"

6. **Crear página**

### 1.3 Completar la Página

Una vez creada:
- Añade banner/cover image
- Completa secciones adicionales
- Publica un post de bienvenida explicando el propósito

⚠️ **Importante:** Guarda el **Page ID** - lo necesitarás más adelante.

**Para obtener el Page ID:**
- Ve a tu página
- Click en "Admin tools" > "Page details"
- Busca la URL: `https://www.linkedin.com/company/[PAGE_ID]/`
- O usa: https://www.linkedin.com/company/[tu-page-url]/admin/

El Page ID es el número que aparece en la URL.

---

## 🔧 PASO 2: Crear App en LinkedIn Developer Portal

### 2.1 Ir al Developer Portal

**URL:** https://www.linkedin.com/developers/apps

### 2.2 Crear Nueva App

1. Click en **"Create app"**
2. **Información de la app:**
   - **App name:** `WebIAScraperNewsBot`
   - **LinkedIn Page:** Selecciona la página que creaste arriba
   - **App logo:** Sube el mismo logo de la página
   - **Legal agreement:** Acepta los términos

3. **Click:** "Create app"

### 2.3 Configurar App Settings

Una vez creada, irás a la página de la app.

**Tabs importantes:**
- **Settings:** Información básica
- **Products:** Permisos que necesitas solicitar
- **Auth:** Configuración OAuth 2.0

---

## 🔐 PASO 3: Solicitar Permisos (Products)

LinkedIn controla estrictamente qué apps pueden hacer qué cosas.

### 3.1 Ir a Tab "Products"

Necesitas solicitar acceso a:

**1. Share on LinkedIn** (ESENCIAL)
- Permite publicar en nombre de la página
- Otorga permisos: `w_member_social`, `w_organization_social`

**2. Sign In with LinkedIn using OpenID Connect** (OPCIONAL)
- Para autenticación de usuarios
- Permisos: `openid`, `profile`, `email`

### 3.2 Solicitar "Share on LinkedIn"

1. Click en **"Share on LinkedIn"**
2. Click **"Request access"**
3. **Completar formulario:**

**Why do you need this product?**
```
We are building an automated news aggregation service that shares
AI and Data Science news summaries in Spanish on our LinkedIn Company Page.

The bot:
- Aggregates tech news from public sources
- Creates summaries using AI
- Translates to Spanish for Hispanic professionals
- Posts to our company page with full source attribution
- Includes direct links to original articles
- Educational and non-commercial purpose

This helps democratize access to AI news for Spanish-speaking professionals.
```

**How will you use member data?**
```
We will NOT collect or store any member data. The app only posts
content to our own Company Page. No user data is accessed or stored.
```

4. **Submit**

### 3.3 Esperar Aprobación

⏰ **Tiempo de aprobación:** 1-7 días (puede ser más)

LinkedIn revisará tu solicitud. Recibirás un email en schaller.ponce@gmail.com cuando sea aprobada o si necesitan más información.

**Mientras esperas:** Puedes continuar configurando el resto, pero NO podrás publicar hasta que aprueben.

---

## 🔑 PASO 4: Configurar OAuth 2.0

LinkedIn usa OAuth 2.0, que es más complejo que las otras plataformas porque requiere un **redirect URL**.

### 4.1 OAuth 2.0 Flow

El proceso es:
1. **Autorización:** Usuario (tú) autoriza la app via navegador
2. **Callback:** LinkedIn redirige a tu URL con un `code`
3. **Exchange:** Intercambias el `code` por un `access_token`
4. **Uso:** Usas el `access_token` para publicar

### 4.2 Configurar Redirect URL

En la tab **"Auth"** de tu app:

**OAuth 2.0 settings:**
- **Redirect URLs:** Añade: `http://localhost:8080/callback`

⚠️ Para testing local, LinkedIn permite `localhost`. Para producción necesitarás un dominio real con HTTPS.

### 4.3 Obtener Client ID y Client Secret

En la misma tab **"Auth"**:
- **Client ID:** Copiar y guardar
- **Client Secret:** Copiar y guardar (solo se muestra una vez)

**Guardar temporalmente en:** `linkedin_credentials_TEMP.txt`
```
Client ID: [tu_client_id]
Client Secret: [tu_client_secret]
Page ID: [tu_page_id]
```

---

## 🔐 PASO 5: Obtener Access Token (MANUAL)

Este es el paso más complejo. LinkedIn requiere que:
1. Autorices la app manualmente en el navegador
2. Captures el `code` del callback
3. Intercambies el `code` por un `access_token`

### 5.1 Construir URL de Autorización

Usa esta URL (reemplaza `YOUR_CLIENT_ID`):

```
https://www.linkedin.com/oauth/v2/authorization?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=http://localhost:8080/callback&scope=openid%20profile%20email%20w_member_social%20w_organization_social
```

**Parámetros:**
- `response_type=code`: Queremos un código
- `client_id=YOUR_CLIENT_ID`: Tu Client ID
- `redirect_uri=http://localhost:8080/callback`: Donde LinkedIn redirigirá
- `scope=openid profile email w_member_social w_organization_social`: Permisos

### 5.2 Abrir URL en Navegador

1. Reemplaza `YOUR_CLIENT_ID` con tu Client ID real
2. Abre la URL en el navegador
3. **LinkedIn te pedirá:** "Allow [App Name] to access your LinkedIn account?"
4. **Click:** "Allow"

### 5.3 Capturar el Code

LinkedIn redirigirá a: `http://localhost:8080/callback?code=AQT...&state=...`

⚠️ **Verás un error de "página no disponible"** - ¡Esto es NORMAL! Localhost:8080 no está corriendo.

**Importante:** Copia el parámetro `code` de la URL. Ejemplo:
```
http://localhost:8080/callback?code=AQTxKz...ABC&state=...
```

Copia solo: `AQTxKz...ABC` (todo entre `code=` y `&`)

### 5.4 Intercambiar Code por Access Token

Usa `curl` para intercambiar el código:

```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=TU_CODE_AQUI" \
  -d "client_id=TU_CLIENT_ID" \
  -d "client_secret=TU_CLIENT_SECRET" \
  -d "redirect_uri=http://localhost:8080/callback"
```

**Reemplaza:**
- `TU_CODE_AQUI`: El code que capturaste
- `TU_CLIENT_ID`: Tu Client ID
- `TU_CLIENT_SECRET`: Tu Client Secret

**Respuesta:**
```json
{
  "access_token": "AQV...",
  "expires_in": 5184000,
  "refresh_token": "AQX...",
  "refresh_token_expires_in": 31536000,
  "scope": "..."
}
```

**Guardar:**
- `access_token`: Token para hacer requests
- `refresh_token`: Para renovar cuando expire
- `expires_in`: Segundos hasta que expire (60 días típicamente)

### 5.5 Obtener Person URN

Necesitas tu **Person URN** para identificarte:

```bash
curl -X GET https://api.linkedin.com/v2/userinfo \
  -H "Authorization: Bearer TU_ACCESS_TOKEN"
```

**Respuesta:**
```json
{
  "sub": "abc123xyz",
  "name": "Tu Nombre",
  "email": "schaller.ponce@gmail.com"
}
```

El `sub` es tu **Person ID**. Tu URN será: `urn:li:person:abc123xyz`

---

## ⚙️ PASO 6: Configurar en el Proyecto

### 6.1 Editar .env.social_publisher

```bash
nano .env.social_publisher
```

### 6.2 Añadir Credenciales de LinkedIn

```bash
# ============================================================================
# LINKEDIN CREDENTIALS
# ============================================================================
LINKEDIN_CLIENT_ID=tu_client_id_aqui
LINKEDIN_CLIENT_SECRET=tu_client_secret_aqui
LINKEDIN_ACCESS_TOKEN=tu_access_token_aqui
LINKEDIN_PERSON_URN=urn:li:person:abc123xyz  # Tu Person URN
```

### 6.3 Habilitar LinkedIn

Actualizar la línea de plataformas:

```bash
ENABLED_PLATFORMS=telegram,bluesky,twitter,linkedin
```

Guardar (Ctrl+O, Enter, Ctrl+X)

---

## 🧪 PASO 7: Probar Publicación

### 7.1 Reiniciar Social Publisher

```bash
docker-compose stop social_publisher
docker-compose rm -f social_publisher
docker-compose up -d social_publisher
```

### 7.2 Ver Logs

```bash
docker-compose logs -f social_publisher
```

Buscar:
```
✅ LinkedIn: Adaptador inicializado
✅ Plataformas configuradas: telegram, bluesky, twitter, linkedin
```

### 7.3 Publicar Noticia de Prueba

1. Ir a http://localhost:8000
2. Añadir nueva noticia
3. Procesarla
4. Esperar ~60 segundos

### 7.4 Verificar en LinkedIn

Ve a tu LinkedIn Page y verifica que apareció el post.

---

## ⚠️ PROBLEMAS COMUNES

### Problema 1: "Products access not granted"
**Causa:** LinkedIn aún no aprobó tu solicitud de "Share on LinkedIn"

**Solución:**
- Esperar aprobación
- Verificar email para mensajes de LinkedIn
- Revisar status en Developer Portal > Products

### Problema 2: "Invalid redirect_uri"
**Causa:** La redirect URI no coincide exactamente

**Solución:**
- Verificar que usaste exactamente: `http://localhost:8080/callback`
- Sin trailing slash
- Sin https en localhost

### Problema 3: "Access token expired"
**Causa:** Los access tokens de LinkedIn expiran (típicamente 60 días)

**Solución:**
- Usar refresh token para obtener nuevo access token
- O repetir el flow OAuth manualmente

**Para renovar con refresh token:**
```bash
curl -X POST https://www.linkedin.com/oauth/v2/accessToken \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=TU_REFRESH_TOKEN" \
  -d "client_id=TU_CLIENT_ID" \
  -d "client_secret=TU_CLIENT_SECRET"
```

### Problema 4: "Organization not found"
**Causa:** El Page ID es incorrecto o no tienes permisos admin

**Solución:**
- Verificar que eres admin de la página
- Confirmar el Page ID correcto
- Usar Organization URN: `urn:li:organization:[PAGE_ID]`

---

## 📊 Límites de LinkedIn

| Característica | Límite |
|----------------|--------|
| Posts por día | ~25-30 (no documentado oficialmente) |
| Caracteres por post | 3,000 |
| Hashtags recomendados | 3-5 |
| Rate limit | Varía, usar con moderación |

**Para tu caso:**
- 3-5 noticias/día es seguro
- No exceder 20 posts/día

---

## 🔒 Seguridad

### ⚠️ NUNCA Compartas:
- Client ID (relativamente seguro, pero mejor no)
- Client Secret (MUY SENSIBLE)
- Access Token
- Refresh Token
- Person URN

### ✅ Buenas Prácticas:
- Mantener `.env.social_publisher` en `.gitignore`
- Regenerar tokens si sospechas compromiso
- Renovar access tokens antes de que expiren
- Monitorear actividad en la página

---

## 🎨 Personalización del Formato

El adaptador de LinkedIn ya está implementado en:
`social_publisher/adapters/linkedin.py`

Formato actual:
- Título en negrita
- Resumen
- Fuente identificada
- Link al original
- Hashtags relevantes
- Disclaimer

Para personalizar, edita el método `format_content()` en `linkedin.py`

---

## 📝 Checklist Final

Antes de ir a producción con LinkedIn:

- [ ] LinkedIn Company Page creada
- [ ] Page ID obtenido
- [ ] App creada en LinkedIn Developers
- [ ] Producto "Share on LinkedIn" solicitado
- [ ] "Share on LinkedIn" APROBADO por LinkedIn
- [ ] Client ID y Client Secret obtenidos
- [ ] OAuth flow completado manualmente
- [ ] Access Token obtenido
- [ ] Refresh Token guardado
- [ ] Person URN obtenido
- [ ] Credenciales configuradas en `.env.social_publisher`
- [ ] LinkedIn habilitado en `ENABLED_PLATFORMS`
- [ ] Social Publisher reiniciado
- [ ] Logs muestran "LinkedIn: Adaptador inicializado"
- [ ] Primera publicación de prueba exitosa
- [ ] Página de LinkedIn actualizada con descripción completa

---

## 🔄 Renovación Automática de Tokens (Futuro)

Actualmente, el token debe renovarse manualmente. Para automatizar:

1. Guardar `refresh_token` en `.env.social_publisher`
2. Implementar lógica en `linkedin.py` para:
   - Detectar cuando access_token está por expirar
   - Usar refresh_token para obtener nuevo access_token
   - Guardar nuevo access_token automáticamente

Esto es una mejora futura, por ahora el token dura 60 días.

---

## 💡 Tips Importantes

1. **Page vs Profile:** Recuerda que publicas en la PAGE, no en tu perfil personal
2. **Aprobación lenta:** LinkedIn puede tardar días en aprobar
3. **Tokens expiran:** A diferencia de Twitter, necesitarás renovar
4. **Profesionalismo:** LinkedIn es más estricto con contenido spam
5. **Engagement:** LinkedIn premia contenido de calidad con más alcance

---

## 📞 ¿Necesitas Ayuda?

**Si tienes problemas:**
1. Revisa la sección "Problemas Comunes"
2. Verifica logs: `docker-compose logs social_publisher`
3. Consulta documentación oficial: https://docs.microsoft.com/en-us/linkedin/
4. Contacto proyecto: schaller.ponce@gmail.com

---

## 🔗 Enlaces Útiles

- **LinkedIn Pages:** https://www.linkedin.com/company/setup/new/
- **Developer Portal:** https://www.linkedin.com/developers/apps
- **Documentación API:** https://docs.microsoft.com/en-us/linkedin/
- **OAuth 2.0 Guide:** https://docs.microsoft.com/en-us/linkedin/shared/authentication/
- **Share API:** https://docs.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/

---

## 🚀 Después de LinkedIn

Una vez LinkedIn funcione, tendrás las **4 plataformas principales activas**:
- ✅ Telegram
- ✅ Bluesky
- ✅ Twitter/X
- ✅ LinkedIn

**Próximos pasos sugeridos:**
1. Campaña de promoción en tus redes personales
2. Ajustar intervalo de polling a producción (300s)
3. Monitorear engagement y ajustar contenido
4. Implementar renovación automática de tokens LinkedIn
5. Considerar analytics y métricas

---

**¡Buena suerte con LinkedIn!** 💼🚀

---

**Última actualización:** 20 de Noviembre de 2025
