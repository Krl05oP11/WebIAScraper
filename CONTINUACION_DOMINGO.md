# 📋 Documento de Continuidad - Sesión Domingo

**Fecha:** 2025-11-21
**Última sesión:** Viernes por la noche
**Próxima sesión:** Domingo por la mañana
**Estado:** Rediseño UX en progreso (40% completado)

---

## 🎯 Objetivo General

Implementar un **flujo mejorado de publicación** que separe claramente:
1. **Procesamiento con Claude** (traducción + resúmenes)
2. **Publicación en RRSS** (envío a plataformas seleccionadas)

Con sistema de reintentos automáticos, monitoreo visual en tiempo real, y gestión inteligente de errores.

---

## ✅ Progreso Completado

### 1. **Base de Datos Actualizada** ✅

**Archivo:** `src/models.py`

**Nuevos campos agregados a tabla `apublicar`:**

```sql
-- Campos agregados y migrados exitosamente
fase VARCHAR(50) DEFAULT 'pendiente'
contador_reintentos INTEGER DEFAULT 0
ultimo_intento TIMESTAMP
proximo_reintento TIMESTAMP
expires_at TIMESTAMP
```

**Estados posibles de `fase`:**
- `pendiente` - En cola, sin procesar
- `procesando` - Claude procesando ahora
- `procesado` - Traducción/resumen completo, listo para publicar
- `publicando` - Enviando a RRSS
- `publicado_parcial` - Algunas plataformas OK, otras fallaron
- `publicado_completo` - Todas las plataformas OK
- `fallido` - Error irrecuperable

**Migración ejecutada:**
```bash
docker-compose exec -T db psql -U webiauser -d webiascrap -c "ALTER TABLE apublicar ADD COLUMN..."
# ✅ Completado exitosamente
```

---

### 2. **Prototipo HTML Completo** ✅

**Archivo:** `prototipo_nuevo_flujo.html`

**Características implementadas:**
- ✅ Checkboxes de plataformas siempre visibles
- ✅ Botón de eliminación (🗑️) por noticia
- ✅ Semáforo animado (🟡 parpadeante, 🟢 OK, 🔴 error, ⚪ no seleccionado)
- ✅ Contador regresivo animado (60/60s → 0/60s)
- ✅ Contador de reintentos visible (1/3, 2/3, 3/3)
- ✅ Botón "PUBLICAR Seleccionadas" que se habilita/deshabilita según selección

**Estados demostrados:**
1. Pendiente de procesar
2. Procesada, esperando publicación
3. Publicando (con contador activo)
4. Publicación parcial con reintentos
5. Publicado exitosamente

**Para revisar:**
```bash
firefox prototipo_nuevo_flujo.html
# o doble clic en el archivo
```

---

### 3. **Backend Parcialmente Actualizado** ⚠️

**Archivos modificados:**

**`social_publisher/publisher_service.py`** (líneas 331-345)
- ✅ Ahora respeta `plataformas_seleccionadas` de cada noticia
- ✅ Filtra plataformas disponibles antes de publicar

**`src/app.py`**
- ✅ Endpoint `procesar_noticia()` actualizado para guardar plataformas seleccionadas
- ⚠️ FALTA: Endpoint separado para publicación sin procesamiento

**`src/templates/apublicar.html`**
- ✅ Botón "PUBLICAR Seleccionadas" agregado en header
- ⚠️ FALTA: Implementar checkboxes siempre visibles (actualmente solo visible al hacer clic en "Procesar")

---

### 4. **Commits y Repositorio** ✅

**GitHub:** https://github.com/Krl05oP11/WebIAScraper

**Commits creados:**
1. `3c6d292` - SocialPublisher microservice con Telegram
2. `4b5d4e2` - Guía de continuación para Telegram
3. `2922732` - Sistema multi-plataforma completo (4 redes sociales)
4. `d401cc0` - Rediseño UX para separar procesamiento y publicación (WIP)
5. `f504ac2` - Prototipo HTML del nuevo flujo de publicación
6. `32c9ba2` - Limpieza: removido archivo con credenciales

**Estado:**
- ✅ Push exitoso a GitHub
- ✅ Credenciales removidas del historial
- ✅ Todos los cambios guardados

---

## 🚧 Tareas Pendientes (Para Domingo)

### **Prioridad ALTA (Implementar primero)**

#### 1. **Actualizar UI de `apublicar.html`** 🎨

**Objetivo:** Mostrar checkboxes de plataformas siempre visibles (basado en prototipo aprobado)

**Archivo a modificar:** `src/templates/apublicar.html`

**Cambios requeridos:**

```html
<!-- REEMPLAZAR la sección actual (líneas 80-128) -->
<!-- POR: Checkboxes siempre visibles con ID único por noticia -->

<div class="platforms-selector" style="margin-bottom: 1rem;">
    <h4>📡 Selecciona plataformas para publicar:</h4>
    <div class="platforms-grid">
        <label class="platform-checkbox">
            <input type="checkbox"
                   name="platform_{{ noticia.id }}_telegram"
                   value="telegram"
                   data-noticia="{{ noticia.id }}"
                   onchange="updatePublishButton()"
                   {% if noticia.plataformas_seleccionadas and 'telegram' in noticia.plataformas_seleccionadas %}checked{% endif %}>
            <span>📱 Telegram</span>
        </label>
        <!-- Repetir para: bluesky, twitter, linkedin (disabled) -->
    </div>
</div>

<!-- Agregar semáforo de estado (líneas 149-200 actuales mantener pero mejorar) -->
```

**JavaScript necesario:**
```javascript
function updatePublishButton() {
    // Contar cuántas noticias tienen al menos 1 checkbox marcado
    const checkboxes = document.querySelectorAll('input[type="checkbox"][data-noticia]:checked');
    const btnPublicar = document.getElementById('btn-publicar-seleccionadas');
    btnPublicar.disabled = checkboxes.length === 0;
}
```

---

#### 2. **Crear Endpoint de Publicación Separado** 🔧

**Archivo a modificar:** `src/app.py`

**Nuevo endpoint requerido:**

```python
@app.route('/publicar-seleccionadas', methods=['POST'])
@csrf.exempt  # Para social_publisher
def publicar_seleccionadas():
    """
    Publicar noticias seleccionadas en plataformas elegidas

    NO procesa con Claude - solo publica
    Noticias deben estar en fase 'procesado' o superior

    Request JSON:
    {
        "noticias": [
            {
                "id": 123,
                "platforms": ["telegram", "bluesky"]
            }
        ]
    }

    Response JSON:
    {
        "success": true,
        "resultados": {
            "123": {
                "telegram": {"success": true, "post_url": "..."},
                "bluesky": {"success": false, "error": "..."}
            }
        }
    }
    """
    try:
        data = request.get_json()
        noticias_data = data.get('noticias', [])

        resultados = {}

        for noticia_data in noticias_data:
            noticia_id = noticia_data['id']
            platforms = noticia_data['platforms']

            # Obtener noticia de BD
            noticia = APublicar.query.get(noticia_id)

            if not noticia:
                resultados[noticia_id] = {"error": "Noticia no encontrada"}
                continue

            # Verificar que esté procesada
            if not noticia.procesado:
                resultados[noticia_id] = {"error": "Noticia no procesada con Claude"}
                continue

            # Actualizar fase y plataformas seleccionadas
            noticia.fase = 'publicando'
            noticia.plataformas_seleccionadas = platforms
            noticia.ultimo_intento = datetime.utcnow()
            db.session.commit()

            # Inicializar plataformas_publicadas si no existe
            if not noticia.plataformas_publicadas:
                noticia.plataformas_publicadas = {}

            # TODO: Aquí llamar al social_publisher para publicar
            # Por ahora, simular publicación exitosa
            for platform in platforms:
                if platform not in noticia.plataformas_publicadas:
                    noticia.plataformas_publicadas[platform] = {}

                noticia.plataformas_publicadas[platform]['status'] = 'pending'
                noticia.plataformas_publicadas[platform]['intentos'] = 0

            db.session.commit()

            resultados[noticia_id] = {"queued": True, "platforms": platforms}

        return jsonify({
            'success': True,
            'resultados': resultados
        })

    except Exception as e:
        logger.error(f"Error en publicar_seleccionadas: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
```

**IMPORTANTE:** Este endpoint solo INICIA la publicación. La publicación real la hace el `social_publisher` de forma asíncrona.

---

#### 3. **Implementar Monitoreo en Tiempo Real** ⏱️

**Objetivo:** Mostrar progreso de publicación con contador regresivo

**Opciones de implementación:**

**Opción A: Polling (Más simple)**
```javascript
// En apublicar.html
function monitorearPublicacion(noticiaId) {
    const intervalo = setInterval(async () => {
        const response = await fetch(`/api/status/${noticiaId}`);
        const data = await response.json();

        // Actualizar UI con estado actual
        actualizarSemaforo(noticiaId, data);

        // Si completó (éxito o error), detener polling
        if (data.fase === 'publicado_completo' || data.fase === 'publicado_parcial') {
            clearInterval(intervalo);
        }
    }, 2000); // Cada 2 segundos
}
```

**Opción B: Server-Sent Events (Más eficiente)**
```python
# En app.py
@app.route('/api/status-stream/<int:noticia_id>')
def status_stream(noticia_id):
    def generate():
        while True:
            noticia = APublicar.query.get(noticia_id)
            data = json.dumps({
                'fase': noticia.fase,
                'plataformas_publicadas': noticia.plataformas_publicadas,
                'contador_reintentos': noticia.contador_reintentos
            })
            yield f"data: {data}\n\n"
            time.sleep(2)

            if noticia.fase in ['publicado_completo', 'publicado_parcial']:
                break

    return Response(generate(), mimetype='text/event-stream')
```

**Recomendación:** Empezar con Opción A (polling) por simplicidad. Migrar a B si hay problemas de rendimiento.

---

### **Prioridad MEDIA**

#### 4. **Sistema de Reintentos Automáticos** 🔄

**Archivo a crear:** `src/retry_scheduler.py`

**Lógica requerida:**

```python
"""
Scheduler para reintentos automáticos de publicaciones fallidas

Características:
- Ejecuta cada 1 minuto
- Busca noticias con proximo_reintento <= ahora
- Reintenta solo si contador_reintentos < 3
- Incrementa contador_reintentos
- Calcula proximo_reintento (10 minutos después)
"""

import schedule
import time
from datetime import datetime, timedelta
from models import db, APublicar

def procesar_reintentos():
    """Procesar reintentos pendientes"""
    ahora = datetime.utcnow()

    # Buscar noticias pendientes de reintento
    noticias = APublicar.query.filter(
        APublicar.proximo_reintento <= ahora,
        APublicar.contador_reintentos < 3,
        APublicar.fase.in_(['publicado_parcial', 'fallido'])
    ).all()

    for noticia in noticias:
        # Identificar plataformas fallidas
        plataformas_fallidas = []
        for platform, info in noticia.plataformas_publicadas.items():
            if info.get('status') == 'error':
                plataformas_fallidas.append(platform)

        if plataformas_fallidas:
            # Reintentar publicación
            # TODO: Llamar a social_publisher

            # Incrementar contador
            noticia.contador_reintentos += 1
            noticia.ultimo_intento = ahora

            # Si todavía hay reintentos disponibles
            if noticia.contador_reintentos < 3:
                noticia.proximo_reintento = ahora + timedelta(minutes=10)

            db.session.commit()

# Ejecutar cada minuto
schedule.every(1).minutes.do(procesar_reintentos)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(30)
```

**Integración con Docker:**

Agregar servicio en `docker-compose.yml`:
```yaml
retry_scheduler:
  build: .
  command: python src/retry_scheduler.py
  depends_on:
    - db
    - app
  environment:
    - DATABASE_URL=postgresql://webiauser:${DB_PASSWORD}@db:5432/webiascrap
```

---

#### 5. **Auto-eliminación de Noticias Viejas** 🗑️

**Archivo a crear:** `src/cleanup_scheduler.py`

```python
"""
Scheduler para auto-eliminación de noticias después de 2 días
"""

import schedule
import time
from datetime import datetime
from models import db, APublicar

def limpiar_noticias_viejas():
    """Eliminar noticias con expires_at < ahora"""
    ahora = datetime.utcnow()

    noticias_viejas = APublicar.query.filter(
        APublicar.expires_at <= ahora
    ).all()

    count = 0
    for noticia in noticias_viejas:
        db.session.delete(noticia)
        count += 1

    db.session.commit()

    if count > 0:
        print(f"🗑️ Eliminadas {count} noticias expiradas")

# Ejecutar cada 6 horas
schedule.every(6).hours.do(limpiar_noticias_viejas)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(3600)  # 1 hora
```

---

### **Prioridad BAJA (Mejoras futuras)**

#### 6. **Mejorar Semáforo con Animaciones CSS**

Copiar CSS del prototipo a `src/static/style.css`:

```css
@keyframes blink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
}

.semaforo.blinking {
    animation: blink 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.platform-status.waiting {
    animation: pulse 2s infinite;
}
```

---

## 🗂️ Estructura de Archivos Actual

```
webiascrap_v0.0.0/
├── src/
│   ├── app.py                      # Flask app principal
│   ├── models.py                   # ✅ ACTUALIZADO (nuevos campos)
│   ├── templates/
│   │   └── apublicar.html          # ⚠️ PENDIENTE (actualizar UI)
│   ├── static/
│   │   └── style.css               # Para agregar animaciones
│   └── utils/
│       └── social_media_processor.py  # Procesador Claude
│
├── social_publisher/
│   ├── publisher_service.py        # ✅ ACTUALIZADO (respeta plataformas)
│   ├── adapters/
│   │   ├── telegram.py             # ✅ Funcionando
│   │   ├── bluesky.py              # ✅ Funcionando
│   │   ├── twitter.py              # ✅ Funcionando
│   │   └── linkedin.py             # ⚠️ DESHABILITADO (problema 403)
│   └── main.py                     # Servicio daemon
│
├── docs/
│   └── LINKEDIN_ISSUE_REPORT.md    # Reporte técnico LinkedIn
│
├── prototipo_nuevo_flujo.html      # ✅ PROTOTIPO APROBADO
├── CONTINUACION_DOMINGO.md         # 📄 ESTE ARCHIVO
└── docker-compose.yml
```

---

## 🔧 Comandos Útiles

### **Iniciar Servicios**
```bash
docker-compose up -d
docker-compose logs -f app           # Ver logs de Flask
docker-compose logs -f social_publisher  # Ver logs de publicador
```

### **Conectar a Base de Datos**
```bash
docker-compose exec -T db psql -U webiauser -d webiascrap
```

### **Ver Estado de Noticias**
```sql
SELECT id, LEFT(titulo, 50) as titulo, fase, procesado, contador_reintentos,
       plataformas_seleccionadas
FROM apublicar
ORDER BY selected_at DESC
LIMIT 10;
```

### **Reiniciar App (después de cambios)**
```bash
docker-compose restart app
```

### **Ver Prototipo**
```bash
firefox prototipo_nuevo_flujo.html
# o
google-chrome prototipo_nuevo_flujo.html
```

---

## 📊 Flujo Completo del Usuario (Diseño Final)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. PÁGINA PRINCIPAL - Noticias Disponibles                 │
│    - Usuario marca checkboxes de noticias que le interesan │
│    - Clic en "Copiar seleccionadas a A Publicar"           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. PÁGINA "A PUBLICAR" - Cola de Publicación               │
│                                                             │
│    ┌───────────────────────────────────────────────┐       │
│    │ Noticia 1: [⏳ Pendiente de procesar]         │       │
│    │ ☐ Telegram  ☐ Bluesky  ☐ Twitter  ☐ LinkedIn │       │
│    │ [🤖 Procesar con Claude]                      │       │
│    └───────────────────────────────────────────────┘       │
│                                                             │
│    ┌───────────────────────────────────────────────┐       │
│    │ Noticia 2: [✅ Procesado con Claude]          │       │
│    │ ☑ Telegram  ☑ Bluesky  ☐ Twitter  ☐ LinkedIn │       │
│    └───────────────────────────────────────────────┘       │
│                                                             │
│    [📤 PUBLICAR Seleccionadas] ← Se habilita si hay ☑     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (Usuario hace clic en PUBLICAR)
┌─────────────────────────────────────────────────────────────┐
│ 3. PUBLICACIÓN EN PROGRESO                                 │
│                                                             │
│    Noticia 2: [📤 Publicando...]                           │
│    🟡 Telegram  [45/60s]  ← Parpadeante                    │
│    🟢 Bluesky   [🔗]      ← OK                             │
│    ⚪ Twitter             ← No seleccionado                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (Después de 60s o confirmación)
┌─────────────────────────────────────────────────────────────┐
│ 4. RESULTADO FINAL                                         │
│                                                             │
│    ✅ Noticia 2: [Publicado exitosamente]                  │
│    🟢 Telegram  [🔗]                                        │
│    🟢 Bluesky   [🔗]                                        │
│    ⚪ Twitter   [No seleccionado]                          │
│                                                             │
│    O si hay error:                                         │
│                                                             │
│    ⚠️ Noticia 2: [Publicación parcial - Reintentando]     │
│    🔄 Reintento automático 2/3 - Próximo en 8:45 min      │
│    🟢 Telegram  [🔗]                                        │
│    🔴 Bluesky   [⚠️] ← Error: Connection timeout  [2/3]   │
│    ⚪ Twitter   [No seleccionado]                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 Notas Importantes

### **LinkedIn - Estado Actual**
- ⚠️ **TEMPORALMENTE DESHABILITADO**
- **Problema:** Error 403 ACCESS_DENIED en campo `/author`
- **Causa:** Scope `w_member_social` insuficiente para validar author
- **Solución pendiente:** Contactar LinkedIn Support o aplicar a Community Management API
- **Documentación:** `docs/LINKEDIN_ISSUE_REPORT.md`
- **En UI:** Mostrar checkbox deshabilitado con "(próximamente)"

### **Plataformas Funcionando**
- ✅ **Telegram:** Funcionando perfectamente
- ✅ **Bluesky:** Funcionando perfectamente
- ✅ **Twitter/X:** Funcionando perfectamente

### **Credenciales**
- ⚠️ **NO commitear** archivos `.env` ni credenciales
- ✅ Ya están en `.gitignore`
- ✅ Archivo `CONTINUACION_LINKEDIN.md` removido del historial

### **Base de Datos**
- ✅ Migración ejecutada correctamente
- ✅ Nuevos campos funcionando
- ✅ Datos antiguos preservados con valores por defecto

---

## 🎯 Plan de Trabajo para el Domingo

### **Sesión Estimada: 3-4 horas**

**Hora 1 (Setup y UI):**
1. ✅ Revisar este documento
2. ✅ Abrir prototipo HTML para tener referencia
3. 🔧 Implementar checkboxes siempre visibles en `apublicar.html`
4. 🔧 Agregar JavaScript para habilitar/deshabilitar botón PUBLICAR

**Hora 2 (Backend):**
1. 🔧 Crear endpoint `/publicar-seleccionadas`
2. 🔧 Probar publicación manual desde UI
3. 🔧 Verificar actualización de estados en BD

**Hora 3 (Monitoreo):**
1. 🔧 Implementar polling para monitoreo en tiempo real
2. 🔧 Agregar contador regresivo (60/60s)
3. 🔧 Actualizar semáforo dinámicamente

**Hora 4 (Reintentos - Opcional):**
1. 🔧 Implementar `retry_scheduler.py` (si hay tiempo)
2. 🔧 Probar reintentos automáticos
3. 🔧 Implementar `cleanup_scheduler.py` (si hay tiempo)

---

## 🚀 Cómo Retomar el Trabajo

### **1. Abrir Proyecto**
```bash
cd /home/carlos/Projects/webiascrap_v0.0.0
```

### **2. Leer este Documento**
```bash
cat CONTINUACION_DOMINGO.md | less
# o
code CONTINUACION_DOMINGO.md  # Si usas VS Code
```

### **3. Ver Prototipo**
```bash
firefox prototipo_nuevo_flujo.html
```

### **4. Iniciar Servicios**
```bash
docker-compose up -d
docker-compose logs -f app
```

### **5. Abrir Editor de Código**
Archivos clave a tener abiertos:
- `src/templates/apublicar.html` (principal a modificar)
- `src/app.py` (agregar endpoint)
- `prototipo_nuevo_flujo.html` (referencia de diseño)
- `src/models.py` (ver campos disponibles)

### **6. Comenzar con Primera Tarea**
Ver sección **"Prioridad ALTA - Tarea 1"** arriba

---

## 📞 Contacto y Recursos

### **Repositorio GitHub**
https://github.com/Krl05oP11/WebIAScraper

### **Documentación Oficial**
- Telegram Bot API: https://core.telegram.org/bots/api
- Bluesky AT Protocol: https://docs.bsky.app/
- Twitter API v2: https://developer.twitter.com/en/docs/twitter-api
- LinkedIn API: https://learn.microsoft.com/en-us/linkedin/

### **Stack Técnico**
- **Backend:** Python 3.11 + Flask
- **DB:** PostgreSQL 15
- **ORM:** SQLAlchemy
- **AI:** Anthropic Claude 3.5 Sonnet
- **Containers:** Docker + Docker Compose

---

## ✨ Resumen Ejecutivo

**Lo que funciona:**
- ✅ Sistema de scraping de noticias
- ✅ Procesamiento con Claude (traducción + resúmenes)
- ✅ Publicación en Telegram, Bluesky, Twitter
- ✅ Base de datos con nuevos campos
- ✅ Prototipo HTML del nuevo flujo

**Lo que falta implementar:**
- ⚠️ UI con checkboxes siempre visibles
- ⚠️ Endpoint de publicación separado
- ⚠️ Monitoreo en tiempo real con contador
- ⚠️ Sistema de reintentos automáticos
- ⚠️ Auto-eliminación después de 2 días

**Prioridad para el Domingo:**
1. **UI completa** (checkboxes + semáforo + contador)
2. **Endpoint de publicación** separado del procesamiento
3. **Monitoreo en tiempo real** con polling

**Tiempo estimado:** 3-4 horas de trabajo concentrado

---

## 📅 Timeline Estimado

```
Domingo Mañana (09:00 - 13:00):
├─ 09:00 - 10:00  UI: Checkboxes siempre visibles
├─ 10:00 - 11:00  Backend: Endpoint de publicación
├─ 11:00 - 12:00  Frontend: Monitoreo en tiempo real
└─ 12:00 - 13:00  Testing y ajustes finales

Domingo Tarde (Opcional - si hay tiempo):
├─ 15:00 - 16:00  Sistema de reintentos
├─ 16:00 - 17:00  Auto-eliminación
└─ 17:00 - 18:00  Documentación y commit final
```

---

**Última actualización:** 2025-11-21 23:45
**Autor:** Claude Code + Carlos
**Estado:** ✅ Listo para retomar el domingo

---

🚀 **¡Éxito en la próxima sesión!**
