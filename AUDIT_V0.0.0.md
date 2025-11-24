# WebIAScrap v0.0.0 - Auditoría Completa y Cierre de Ciclo
**Fecha**: 2025-11-24
**Versión**: v0.0.0 (MVP)

---

## 📊 ESTADO ACTUAL DE LA APLICACIÓN

### ✅ Componentes Funcionando Correctamente

#### 1. **WebIAScrap (Aplicación Principal)**
- ✅ Scraping automático de noticias (NewsAPI)
- ✅ Almacenamiento en PostgreSQL
- ✅ Interfaz web con Flask
- ✅ Sistema de selección con checkboxes
- ✅ Copia a tabla `apublicar`
- ✅ Procesamiento con Claude AI (traduc resúmenes, hashtags)
- ✅ Sistema de fases (pendiente → procesando → procesado → publicando → publicado)

#### 2. **SocialPublisher (Microservicio de Publicación)**
- ✅ **Telegram**: Funcionando perfectamente (@WebIAScrapperBot)
- ✅ **Bluesky**: Funcionando (schaller-ponce.bsky.social)
- ⏸️ **Twitter/X**: Deshabilitado temporalmente (rate limit 429)
- ❌ **LinkedIn**: Deshabilitado (error 403 ACCESS_DENIED)

#### 3. **Base de Datos**
- ✅ PostgreSQL 15 en Docker
- ✅ Migraciones aplicadas correctamente
- ✅ Modelo `Noticia` - noticias scrapeadas
- ✅ Modelo `APublicar` - queue de publicación con sistema de fases

### 4. **Arquitectura**
```
┌─────────────────┐      ┌──────────────────┐
│   NewsAPI       │─────▶│   WebIAScrap     │
│   (Fuente)      │      │   (Flask App)    │
└─────────────────┘      └──────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │   PostgreSQL     │
                         │   (Base de Datos)│
                         └──────────────────┘
                                   │
                                   ▼
                         ┌──────────────────┐
                         │ SocialPublisher  │
                         │  (Microservicio) │
                         └──────────────────┘
                                   │
          ┌────────────┬──────────┴──────────┬────────────┐
          ▼            ▼                     ▼            ▼
    ┌─────────┐  ┌─────────┐         ┌─────────┐   ┌─────────┐
    │Telegram │  │Bluesky  │         │Twitter  │   │LinkedIn │
    │   ✅    │  │   ✅    │         │   ⏸️    │   │   ❌    │
    └─────────┘  └─────────┘         └─────────┘   └─────────┘
```

---

## 🔍 PROBLEMAS IDENTIFICADOS

### 1. **Hardcodes en Código**

#### `src/models.py:159`
```python
print("✅ Base de datos inicializada correctamente")
```
**Problema**: Uso de `print()` en vez de logging
**Severidad**: Baja
**Fix**: Cambiar a `logger.info()`

#### `src/news_scraper.py:266-276`
Múltiples `print()` en función de testing
**Problema**: Debugging con prints en vez de logs
**Severidad**: Baja
**Fix**: Convertir a logging o mover a función de testing separada

#### `src/social_media_processor.py:294-316`
Estadísticas impresas con `print()`
**Problema**: Salida directa a console en vez de logs
**Severidad**: Baja
**Fix**: Usar logging con nivel INFO

#### `src/technical_sources_scraper.py:362-373`
Similar a news_scraper, prints en testing
**Problema**: Debugging con prints
**Severidad**: Baja
**Fix**: Logging estructurado

#### `src/translation_service.py:269-273`
Prints de resultado de traducción
**Problema**: Debug output
**Severidad**: Baja
**Fix**: Logging con nivel DEBUG

### 2. **Gestión de Tokens Expirados**

**Problema Actual**:
- Bluesky y Twitter autentican al inicio del servicio
- Los tokens JWT expiran después de horas de ejecución
- No hay re-autenticación automática
- Requiere reinicio manual del contenedor

**Impacto**:
- Bluesky falla con "ExpiredToken" después de ~24h
- Twitter acumula errores 429 por reintentos
- Interrumpe la publicación automática

**Solución Necesaria**: Ver sección "Estrategia de Manejo de Tokens"

### 3. **LinkedIn - Error Permanente**

**Estado**: ❌ No funciona
**Error**: `403 ACCESS_DENIED` en campo `/author`
**Causa**: Cambios en API de LinkedIn (2025)
**Documentación**: `docs/LINKEDIN_ISSUE_REPORT.md`
**Solución**: Requiere investigación de nueva API v2 de LinkedIn

### 4. **Twitter/X - Rate Limit Activo**

**Estado**: ⏸️ Temporalmente deshabilitado
**Error**: `429 Too Many Requests`
**Causa**:
- Bug anterior republica misma noticia múltiples veces
- Twitter detectó como spam
- Rate limit activado (15min - 24h)

**Fix Aplicado**:
- Sistema de fases ahora previene republicaciones
- Twitter deshabilitado en `.env.social_publisher`
- Se reactivará mañana cuando se resetee el limite

### 5. **Documentación Desactualizada**

**Archivos que Necesitan Actualización**:
- `README.md` - Menciona LinkedIn como funcional
- `QUICKSTART_SOCIAL_PUBLISHER.md` - No refleja sistema de fases
- Falta documentación de endpoints `/api/status/<id>`

---

## 🔧 MEJORAS IMPLEMENTADAS (Esta Sesión)

### 1. **Sistema de Fases** ✅
- Separación clara: procesamiento con Claude vs publicación en redes
- Estados: pendiente → procesando → procesado → publicando → publicado_parcial/completo/fallido
- Tracking granular por plataforma

### 2. **Monitoreo en Tiempo Real** ✅
- Polling JavaScript cada 2 segundos
- Semáforos animados (🟡 → 🟢/🔴)
- Contador de tiempo transcurrido
- Auto-recarga cuando termina

### 3. **Fix de Bugs Críticos** ✅
- `flag_modified()` para campos JSONB
- Validación robusta de status ('failed' vs 'error')
- Endpoint `/api/news/to-publish` usa sistema de fases
- Checkboxes vacíos al refrescar (no pre-marcados)

### 4. **Gestión de Plataformas** ✅
- Habilitación/deshabilitación dinámica en `.env.social_publisher`
- Re-autenticación automática de Bluesky al reiniciar
- Tracking de errores por plataforma

---

## 🚀 ESTRATEGIA DE MANEJO DE TOKENS EXPIRADOS

### Problema
Las APIs de redes sociales usan tokens con tiempo de vida limitado:
- **Bluesky**: JWT expira después de ~24 horas
- **Twitter**: OAuth tokens pueden expirar
- **LinkedIn**: Access tokens expiran en 60 días

### Solución Propuesta: Auto-Refresh Middleware

#### Opción 1: Re-autenticación Proactiva (Recomendado)
```python
class TokenManager:
    def __init__(self, adapter):
        self.adapter = adapter
        self.last_auth = datetime.utcnow()
        self.token_ttl = timedelta(hours=23)  # Re-auth antes de expirar

    def ensure_authenticated(self):
        """Re-autenticar si el token está por expirar"""
        if datetime.utcnow() - self.last_auth > self.token_ttl:
            logger.info(f"{self.adapter.platform}: Token próximo a expirar, re-autenticando...")
            if self.adapter.authenticate():
                self.last_auth = datetime.utcnow()
                return True
        return self.adapter._authenticated
```

#### Opción 2: Re-autenticación Reactiva
```python
def publish_with_retry(self, content: PostContent) -> PostResult:
    """Publicar con retry automático si falla por token"""
    result = self.publish(content)

    if not result.success and 'expired' in result.error.lower():
        logger.warning(f"{self.platform}: Token expirado, re-autenticando...")
        if self.authenticate():
            result = self.publish(content)  # Retry

    return result
```

#### Implementación para Bluesky
```python
# social_publisher/adapters/bluesky.py
def publish(self, content: PostContent) -> PostResult:
    # Check token age
    if self.token_age() > timedelta(hours=23):
        self.authenticate()  # Refresh

    # ... resto del código
```

### Ventajas
- ✅ No requiere reinicio manual
- ✅ Publicación continua sin interrupciones
- ✅ Logging claro de re-autenticaciones
- ✅ Manejo graceful de errores

---

## 📋 CHECKLIST DE TAREAS PENDIENTES

### Código
- [ ] Reemplazar todos los `print()` por `logger.info/debug()`
- [ ] Implementar TokenManager para auto-refresh
- [ ] Agregar tests para sistema de fases
- [ ] Agregar retry logic mejorado (backoff exponencial)

### Documentación
- [ ] Actualizar README.md con estado actual de plataformas
- [ ] Documentar endpoints de API completos
- [ ] Crear ARCHITECTURE.md con diagramas actualizados
- [ ] Actualizar QUICKSTART con sistema de fases

### Configuración
- [ ] Revisar valores de producción en `.env.example`
- [ ] Documentar proceso de obtención de credentials
- [ ] Crear script de health-check

### Testing
- [ ] Tests para endpoints de publicación
- [ ] Tests para sistema de fases
- [ ] Tests de integración con mocks de APIs

---

## 🔐 PROBLEMAS DE FACEBOOK/INSTAGRAM/THREADS

**Investigación Previa**: `SOCIAL_MEDIA_FEASIBILITY_REPORT.md`

### Facebook
**Estado**: ❌ No viable para automatización
**Razones**:
1. **Graph API requiere revisión de Facebook**
   - Proceso de aprobación de 2-4 semanas
   - Requiere caso de uso empresarial
   - No aceptan bots personales

2. **Publicación requiere App Review**
   - `pages_manage_posts` permission
   - Requiere Página de Facebook (no perfil personal)
   - Revisión manual por Facebook

3. **Limitaciones técnicas**
   - No se puede publicar en perfil personal via API
   - Solo en Páginas de negocio
   - Rate limits muy estrictos

### Instagram
**Estado**: ❌ No viable
**Razones**:
1. **Instagram Graph API es solo para cuentas Business/Creator**
   - No funciona con cuentas personales
   - Requiere conectar a Página de Facebook

2. **Requiere aprobación de permisos**
   - Similar a Facebook
   - Proceso de revisión obligatorio

3. **Limitaciones de contenido**
   - Solo imágenes/videos (no text-only posts)
   - Requiere URL de imagen hosteada

### Threads
**Estado**: ❌ No disponible
**Razones**:
1. **No existe API pública de Threads (2025)**
   - Meta no ha lanzado API oficial
   - No hay forma oficial de publicar programáticamente

2. **Alternativas no viables**
   - Web scraping viola TOS
   - Bots de terceros = ban de cuenta
   - Puppeteer/Selenium = detectable

---

## 🎯 DECISIÓN RECOMENDADA PARA META PLATFORMS

### Opción A: **Abandonar Facebook/Instagram/Threads** (Recomendado)
**Razones**:
- ✅ Telegram y Bluesky funcionan perfectamente
- ✅ Twitter se puede reactivar
- ✅ Evita complejidad de App Review
- ✅ Evita riesgo de ban de cuentas
- ✅ Enfoque en plataformas con APIs abiertas

### Opción B: **Crear Página de Facebook Business** (Si quieres Facebook)
**Requiere**:
- Crear Página de Facebook (no perfil)
- Solicitar App Review de Meta
- Esperar 2-4 semanas de aprobación
- Configurar Business Manager
- Solo funcionará para la Página (no perfil personal)

### Opción C: **Publicación Manual** (Fallback)
- Usar WebIAScrap para generar contenido
- Copiar/pegar manualmente en Facebook/Instagram/Threads
- Simple pero no automatizado

---

## 📝 NOTAS FINALES

### Lo que Funciona Bien
- ✅ Arquitectura de microservicios escalable
- ✅ Sistema de fases robusto
- ✅ Telegram y Bluesky 100% funcionales
- ✅ Monitoreo en tiempo real
- ✅ UI intuitiva y funcional

### Lo que Necesita Mejora
- 🔧 Manejo automático de tokens expirados
- 🔧 Logging en vez de prints
- 🔧 Tests de integración
- 🔧 LinkedIn (investigar API v2)
- 🔧 Documentación actualizada

### Lecciones Aprendidas
1. **APIs de redes sociales son complicadas** - Cada una tiene sus quirks
2. **Token management es crítico** - Necesita ser automático
3. **Rate limiting es real** - Necesita retry inteligente
4. **Meta platforms son cerradas** - Requieren procesos empresariales
5. **SQLAlchemy JSONB** - Necesita `flag_modified()`

---

**Próximos Pasos**: Ver sección de Git Commits y Push
