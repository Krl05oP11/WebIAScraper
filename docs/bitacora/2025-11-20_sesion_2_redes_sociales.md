# 📱 Sesión 2: Configuración de Redes Sociales

**Fecha:** 20 de Noviembre de 2025
**Duración:** ~4 horas
**Objetivos:** Configurar Twitter/X, Bluesky, y preparar LinkedIn

---

## 🎯 Objetivos de la Sesión

1. ✅ Continuar desde sesión anterior (Telegram ya funcionando)
2. ✅ Configurar y probar Twitter/X
3. ✅ Configurar y probar Bluesky
4. ✅ Preparar guía para LinkedIn
5. ✅ Implementar OAuth 1.0a para Twitter
6. ✅ Añadir atribución de fuentes y disclaimers a todas las plataformas

---

## 📝 Resumen de la Conversación

### Inicio de Sesión (Continuación)
- Sistema recuperado desde contexto anterior
- Telegram ya estaba configurado y funcionando
- Base de datos con 8 noticias ya publicadas

### Problema Twitter: OAuth 2.0 vs OAuth 1.0a
1. **Problema inicial:** Twitter API rechazaba autenticación con Bearer Token (403 error)
2. **Causa:** Endpoint `/users/me` requiere OAuth 1.0a o OAuth 2.0 User Context
3. **Solución:** Migrar adaptador de Twitter a OAuth 1.0a
4. **Implementación:**
   - Añadido `requests-oauthlib==1.3.1` a requirements
   - Actualizado método `authenticate()` para usar `OAuth1Session`
   - Actualizado método `publish()` para usar OAuth 1.0a
   - Rebuild del contenedor

### Configuración Twitter
1. Usuario creó cuenta: @SchallerPonceAI
2. Aplicó a Developer Account (Free Tier)
3. Creó app en Developer Portal
4. Generó API Keys y Access Tokens con permisos Read and Write
5. Configuró credenciales en `.env.social_publisher`
6. **Resultado:** ✅ Twitter funcionando correctamente

### Configuración Bluesky
1. Usuario creó cuenta: schaller-ponce.bsky.social
2. Generó app password en Settings
3. Configuró en `.env.social_publisher`
4. **Resultado:** ✅ Bluesky funcionando correctamente

### Pruebas Multi-Plataforma
1. Usuario publicó 2 noticias nuevas
2. Sistema las publicó automáticamente en:
   - ✅ Telegram (mensaje 18 y 19)
   - ✅ Bluesky (2 posts)
   - ✅ Twitter (tweets 1991637172697391150 y 1991637422833037595)
3. Usuario confirmó que todas las publicaciones se ven bien

### Preparación LinkedIn
1. Creada guía completa `SETUP_LINKEDIN.md`
2. Creada guía rápida `LINKEDIN_QUICKSTART.md`
3. Actualizado adaptador de LinkedIn con atribución y disclaimers
4. LinkedIn pendiente de configuración por el usuario

---

## 🛠️ Decisiones Técnicas

### Twitter: OAuth 1.0a vs OAuth 2.0
**Decisión:** Usar OAuth 1.0a en lugar de OAuth 2.0

**Razones:**
1. Tokens no expiran (OAuth 2.0 tokens expiran cada 60 días)
2. No requiere callback server para renovación
3. Más simple para bots automatizados
4. Twitter API v2 soporta OAuth 1.0a perfectamente

**Implementación:**
- `OAuth1Session` de `requests-oauthlib`
- API Key + API Secret + Access Token + Access Token Secret
- Sin necesidad de refresh tokens

### Formato de Publicaciones
**Decisión:** Estandarizar formato en todas las plataformas

**Elementos comunes:**
- 📰 Título (si existe)
- Resumen/descripción
- 📰 Fuente: [nombre del sitio]
- 🔗 Link al artículo original
- Hashtags relevantes
- 📡 Schaller & Ponce AI News
- ℹ️ Disclaimer: "Resumen automático - Todo el crédito al medio original"

**Adaptaciones por plataforma:**
- **Telegram:** HTML formatting, hasta 4096 caracteres
- **Bluesky:** Texto plano, 300 caracteres
- **Twitter:** Texto plano, 280 caracteres
- **LinkedIn:** Texto plano, 3000 caracteres

---

## 🔧 Problemas Encontrados y Soluciones

### 1. Twitter 403 Error con Bearer Token

**Problema:**
```
Twitter: Error de autenticación - 403
```

**Causa:**
- Bearer Token no soportado por endpoint `/users/me`
- Requiere OAuth 1.0a User Context

**Solución:**
1. Añadir `requests-oauthlib==1.3.1`
2. Cambiar autenticación a `OAuth1Session`
3. Usar API Key + Secret + Access Token + Secret
4. Rebuild contenedor

**Archivos modificados:**
- `social_publisher/requirements.txt`
- `social_publisher/adapters/twitter.py`

### 2. Credenciales Twitter con Permisos Incorrectos

**Problema:**
- Access Token inicial tenía solo permisos "Read Only"

**Solución:**
1. Usuario configuró "User authentication settings" en Developer Portal
2. Seleccionó "Read and Write" permissions
3. Regeneró Access Token
4. Credenciales actualizadas funcionaron correctamente

---

## 📊 Lecciones Aprendidas

### OAuth Flows
1. **OAuth 1.0a (Twitter):** Mejor para bots, tokens permanentes
2. **OAuth 2.0 (LinkedIn):** Más moderno pero tokens expiran
3. **App Passwords (Bluesky):** Más simple, ideal para bots

### Rate Limits por Plataforma
- **Telegram:** Sin límites documentados
- **Bluesky:** 300 creates/día, 35 creates/5min
- **Twitter Free:** 1,500 tweets/mes
- **LinkedIn:** ~25-30 posts/día (estimado)

### Aprobaciones
- **Telegram:** Instantáneo
- **Bluesky:** Instantáneo
- **Twitter Free Tier:** Instantáneo (en nuestro caso)
- **LinkedIn:** 1-7 días (requiere revisión manual)

---

## 📁 Archivos Creados/Modificados

### Creados
1. `SETUP_TWITTER_X.md` - Guía completa para configurar Twitter
2. `SETUP_LINKEDIN.md` - Guía completa para configurar LinkedIn
3. `LINKEDIN_QUICKSTART.md` - Guía rápida LinkedIn
4. `X Keys.txt` - Credenciales de Twitter (temporal, no en git)
5. `docs/bitacora/2025-11-20_sesion_2_redes_sociales.md` - Esta bitácora

### Modificados
1. `social_publisher/requirements.txt` - Añadido requests-oauthlib
2. `social_publisher/adapters/twitter.py` - Migrado a OAuth 1.0a
3. `social_publisher/adapters/linkedin.py` - Añadida atribución y disclaimers
4. `.env.social_publisher` - Añadidas credenciales de Twitter y Bluesky

---

## 🔄 Comandos Importantes Ejecutados

### Rebuild Contenedor Twitter
```bash
docker-compose stop social_publisher
docker-compose rm -f social_publisher
docker-compose build social_publisher
docker-compose up -d social_publisher
```

### Ver Logs en Tiempo Real
```bash
docker-compose logs -f social_publisher
```

### Verificar Base de Datos
```bash
docker exec webiascrap_db psql -U webiauser -d webiascrap -c "SELECT id, titulo, publicado, plataformas_publicadas FROM apublicar ORDER BY id;"
```

---

## 📊 Estado Actual del Sistema

### Plataformas Configuradas
- ✅ **Telegram:** @schallerponce - Funcionando
- ✅ **Bluesky:** schaller-ponce.bsky.social - Funcionando
- ✅ **Twitter:** @SchallerPonceAI - Funcionando
- ⏳ **LinkedIn:** Pendiente de configuración

### Noticias Publicadas
- **Total en DB:** 13 noticias
- **Últimas 2 publicadas en:** Telegram, Bluesky, Twitter (multi-plataforma)
- **URLs verificadas:** Usuario confirmó que se ven bien

### Configuración Actual
```bash
ENABLED_PLATFORMS=telegram,bluesky,twitter
POLL_INTERVAL_SECONDS=60  # Testing (cambiar a 300 en producción)
MAX_NEWS_PER_CYCLE=3
```

---

## 🎯 Próximos Pasos

### Inmediato
1. **Usuario:** Configurar LinkedIn siguiendo `SETUP_LINKEDIN.md`
   - Crear LinkedIn Company Page
   - Crear app en Developer Portal
   - Solicitar "Share on LinkedIn" product
   - Esperar aprobación (1-7 días)
   - Completar OAuth flow
   - Probar publicación

### Corto Plazo
2. **Campaña de Promoción:**
   - Anunciar canales en redes personales
   - Invitar contactos a seguir los canales
   - Publicar post de bienvenida en cada plataforma

3. **Optimización:**
   - Cambiar `POLL_INTERVAL_SECONDS=300` (5 minutos en producción)
   - Monitorear engagement
   - Ajustar frecuencia de publicación según respuesta

### Futuro
4. **LinkedIn Token Refresh:**
   - Implementar renovación automática de access tokens
   - Guardar refresh token
   - Detectar expiración y renovar automáticamente

5. **Analytics:**
   - Implementar tracking de métricas
   - Engagement por plataforma
   - Posts más exitosos

6. **Mejoras:**
   - Personalización de formato por tipo de noticia
   - Scheduling de publicaciones
   - Preview de posts antes de publicar

---

## 💡 Notas y Observaciones

### Éxitos
- ✅ OAuth 1.0a implementado correctamente a la primera
- ✅ Multi-plataforma funcionando simultáneamente
- ✅ Formato consistente con atribución en todas las plataformas
- ✅ Usuario siguió proceso paso a paso sin problemas

### Aprendizajes
- Twitter API v2 con OAuth 1.0a es viable y preferible para bots
- Bluesky es sorprendentemente simple de configurar
- LinkedIn será el más complejo por aprobación manual
- Sistema robusto: publicó exitosamente en 3 plataformas simultáneamente

### Para Mejorar
- Documentar proceso de renovación de tokens LinkedIn
- Considerar webhook para notificaciones de publicación
- Implementar retry logic más robusto

---

## 📞 Información de Contacto

**Email del proyecto:** schaller.ponce@gmail.com

**Canales activos:**
- Telegram: @schallerponce
- Bluesky: schaller-ponce.bsky.social
- Twitter: @SchallerPonceAI
- LinkedIn: Pendiente

---

## 🔗 Referencias

### Documentación Utilizada
- Twitter API v2: https://developer.x.com/en/docs/twitter-api
- OAuth 1.0a: https://oauth.net/core/1.0a/
- Bluesky API: https://docs.bsky.app/
- LinkedIn API: https://docs.microsoft.com/en-us/linkedin/

### Guías Creadas
- `SETUP_TWITTER_X.md` - Configuración completa de Twitter
- `SETUP_LINKEDIN.md` - Configuración completa de LinkedIn
- `LINKEDIN_QUICKSTART.md` - Inicio rápido LinkedIn
- `LEGAL_DISCLAIMER.md` - Disclaimer legal del proyecto

---

## ✅ Checklist de Verificación

- [x] Twitter configurado y funcionando
- [x] Bluesky configurado y funcionando
- [x] Publicaciones multi-plataforma verificadas
- [x] Atribución de fuentes implementada
- [x] Disclaimers legales añadidos
- [x] OAuth 1.0a funcionando para Twitter
- [x] Guías de configuración creadas
- [ ] LinkedIn configurado (pendiente - requiere aprobación)
- [ ] Campaña de promoción (pendiente)
- [ ] Ajuste a intervalos de producción (pendiente)

---

**Fin de la sesión 2**
**Próxima sesión:** Configuración de LinkedIn y campaña de promoción

---

**Última actualización:** 20 de Noviembre de 2025
