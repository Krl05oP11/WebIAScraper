# WebIAScrap v0.0.0 - MVP

> Aplicación de web scraping para noticias de Inteligencia Artificial, Ciencia de Datos y Agentes IA

## 📋 Descripción

WebIAScrap es una aplicación web que:
- ✅ Obtiene automáticamente noticias de IA desde múltiples fuentes usando NewsAPI
- ✅ Almacena las 30 noticias más recientes en PostgreSQL
- ✅ Permite visualizar y filtrar noticias por fecha/hora
- ✅ Interfaz con paleta azul oscura para reducir fatiga ocular
- ✅ Sistema de selección con checkboxes para marcar noticias de interés
- ✅ Copia noticias seleccionadas a tabla "APublicar" para procesamiento posterior
- ✅ **NUEVO:** Publicación automatizada en redes sociales (Telegram, Bluesky, Twitter)
- ✅ Sistema de fases: procesamiento separado de publicación
- ✅ Monitoreo en tiempo real con semáforos animados
- ✅ Ejecuta completamente aislado en Docker

## 🚀 Quick Start

### Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- Cuenta gratuita en [NewsAPI](https://newsapi.org/register)

### Instalación y Ejecución

1. **Clonar o navegar al proyecto:**
   ```bash
   cd ~/Projects/webiascrap_v0.0.0
   ```

2. **Obtener API Key de NewsAPI:**
   - Regístrate gratis en https://newsapi.org/register
   - Copia tu API key

3. **Configurar variables de entorno:**
   ```bash
   # El archivo .env ya existe, solo edita la línea de NEWSAPI_KEY
   nano .env

   # Reemplaza esto:
   NEWSAPI_KEY=your-newsapi-key-here

   # Con tu API key real:
   NEWSAPI_KEY=tu-api-key-aqui-abc123xyz
   ```

4. **Iniciar la aplicación con Docker:**
   ```bash
   docker-compose up --build
   ```

5. **Acceder a la aplicación:**
   - Abre tu navegador en: http://localhost:8000
   - La aplicación ejecutará un scraping inicial automáticamente
   - Espera unos segundos para que carguen las noticias

6. **Detener la aplicación:**
   ```bash
   docker-compose down
   ```

## 🎯 Funcionalidades Principales

### 1. Visualización de Noticias
- Lista de las 30 noticias más recientes de IA
- Ordenadas por fecha de publicación
- Cada noticia muestra:
  - Título (clickeable, abre en nueva pestaña)
  - Resumen del contenido
  - Fecha y hora de publicación
  - Temas/keywords extraídos automáticamente
  - Checkbox para selección

### 2. Selección y Copia a "A Publicar"
- Selecciona noticias con checkboxes
- Botón "Seleccionar todo" para marcar todas
- Copia las seleccionadas a tabla `apublicar`
- Vista separada para ver noticias marcadas para publicar

### 3. Scraping Automático
- Se ejecuta cada 24 horas automáticamente
- Mantiene solo las 30 noticias más recientes
- Evita duplicados por URL
- Extrae automáticamente 3-5 temas por noticia

### 4. Scraping Manual
- Botón "🔄 Actualizar Noticias" en el menú
- Ejecuta scraping inmediato bajo demanda

## 📁 Estructura del Proyecto

```
webiascrap_v0.0.0/
├── src/
│   ├── app.py              # Aplicación Flask principal
│   ├── models.py           # Modelos de BD (Noticia, APublicar)
│   ├── news_scraper.py     # Scraper con NewsAPI
│   ├── templates/
│   │   ├── base.html       # Template base
│   │   ├── index.html      # Lista de noticias
│   │   └── apublicar.html  # Noticias seleccionadas
│   └── static/
│       └── css/
│           └── style.css   # Estilos con paleta azul oscura
├── config/
│   └── settings.py         # Configuración de la app
├── tests/
│   ├── test_models.py      # Tests de modelos
│   └── test_scraper.py     # Tests del scraper
├── docker-compose.yml      # Orquestación Docker
├── Dockerfile              # Imagen de la aplicación
├── requirements.txt        # Dependencias Python
├── .env                    # Variables de entorno
└── README.md              # Este archivo
```

## 🗄️ Base de Datos

### Tabla: `noticias`
- `id`: Integer (PK)
- `titulo`: String(500)
- `texto`: Text (hasta 1000 palabras)
- `url`: String(1000) - Unique
- `fecha_hora`: DateTime
- `temas`: String(500) - Temas separados por comas
- `created_at`: DateTime

### Tabla: `apublicar`
- `id`: Integer (PK)
- `titulo`: String(500)
- `texto`: Text
- `url`: String(1000)
- `fecha_hora`: DateTime
- `temas`: String(500)
- `noticia_id`: Integer - Referencia a noticia original
- `selected_at`: DateTime - Cuándo fue seleccionada

## 🧪 Ejecutar Tests

```bash
# Dentro del container
docker-compose exec app pytest

# O localmente (requiere instalar dependencias)
pytest tests/ -v
```

## 🎨 Paleta de Colores (Azul Oscuro)

La interfaz usa una paleta diseñada para reducir fatiga ocular:

- **Fondo primario:** `#0a1929` (azul muy oscuro)
- **Fondo secundario:** `#1a2332` (azul oscuro)
- **Fondo terciario:** `#1e3a5f` (azul medio oscuro)
- **Acento:** `#4a90e2` (azul claro)
- **Texto principal:** `#e8f1f8` (blanco azulado)
- **Texto secundario:** `#a8c5e0` (gris azulado)

## 🔧 Configuración Avanzada

### Cambiar Fuentes de Noticias

Edita `.env`:
```bash
NEWS_SOURCES=techcrunch,wired,the-verge,bbc-news
```

Fuentes disponibles: https://newsapi.org/sources

### Cambiar Keywords de Búsqueda

Edita `.env`:
```bash
NEWS_KEYWORDS=artificial intelligence,robotics,neural networks
```

### Cambiar Intervalo de Scraping

Edita `.env`:
```bash
SCRAPE_INTERVAL_HOURS=12  # Cada 12 horas
```

### Cambiar Número Máximo de Noticias

Edita `.env`:
```bash
MAX_NEWS_COUNT=50  # Guardar hasta 50 noticias
```

## 🐛 Troubleshooting

### Error: "No hay noticias disponibles"

**Causa:** La API key de NewsAPI no está configurada o es inválida

**Solución:**
1. Verifica que hayas reemplazado `NEWSAPI_KEY` en `.env`
2. Verifica tu API key en https://newsapi.org/account
3. Reinicia Docker: `docker-compose restart`

### Error: "Database connection failed"

**Causa:** PostgreSQL no está listo

**Solución:**
1. Espera 10-15 segundos después de `docker-compose up`
2. Verifica logs: `docker-compose logs db`
3. Reinicia: `docker-compose restart`

### Las noticias no se actualizan automáticamente

**Causa:** El scheduler no está funcionando

**Solución:**
1. Usa el botón "Actualizar Noticias" manualmente
2. Verifica logs: `docker-compose logs app`
3. Verifica `SCRAPE_INTERVAL_HOURS` en `.env`

## 📊 API Endpoints

### GET `/api/noticias`
Retorna todas las noticias en formato JSON

```bash
curl http://localhost:8000/api/noticias
```

### GET `/api/apublicar`
Retorna noticias marcadas para publicar en JSON

```bash
curl http://localhost:8000/api/apublicar
```

### GET `/health`
Health check de la aplicación

```bash
curl http://localhost:8000/health
```

## 📱 Publicación Automatizada en Redes Sociales

### **NUEVO en Fase 1:** SocialPublisher Microservice

WebIAScrap ahora incluye un microservicio de publicación automatizada en redes sociales que:

- ✅ Publica automáticamente en **LinkedIn, Twitter/X, Bluesky y Telegram**
- ✅ Sistema de queue interno con retry logic
- ✅ Rate limiting inteligente por plataforma
- ✅ Tracking completo de publicaciones en BD
- ✅ Arquitectura de microservicios escalable

### **Estado Actual de Plataformas** (2025-11-24)

| Plataforma | Estado | Notas |
|------------|--------|-------|
| 📱 **Telegram** | ✅ Funcionando | Bot: @WebIAScrapperBot |
| 🦋 **Bluesky** | ✅ Funcionando | Publicación automática activa |
| 🐦 **Twitter/X** | ⏸️ Pausado | Rate limit temporal, se reactivará |
| 💼 **LinkedIn** | ❌ No disponible | Error 403 API - Requiere investigación |
| 📘 **Facebook** | ❌ No viable | Requiere App Review empresarial |
| 📷 **Instagram** | ❌ No viable | Solo cuentas Business con Page |
| 🧵 **Threads** | ❌ No API | Meta no ha lanzado API pública |

#### Configuración Rápida

1. **Migrar la base de datos:**
   ```bash
   ./migrate_db.sh
   ```

2. **Configurar credenciales:**
   ```bash
   cp .env.social_publisher.example .env.social_publisher
   nano .env.social_publisher  # Completar con tus credenciales
   ```

3. **Iniciar servicios:**
   ```bash
   docker-compose up --build
   ```

#### Documentación Completa

- 📖 [Guía de Configuración Paso a Paso](SETUP_SOCIAL_MEDIA.md)
- 📖 [Documentación del SocialPublisher](social_publisher/README.md)
- 📊 [Informe de Factibilidad de Redes Sociales](SOCIAL_MEDIA_FEASIBILITY_REPORT.md)

## 🚧 Próximas Versiones

### v0.2.0 (Planeada)
- Threads, Facebook y Mastodon adapters (Fase 2)
- Scheduling: publicación en horarios óptimos
- A/B Testing: diferentes formatos de mensaje
- Analytics: tracking de engagement
- Auto-hashtags y auto-imágenes con IA

## 📝 Notas de Desarrollo

- **Python:** 3.11+
- **Framework:** Flask 3.0+
- **Base de datos:** PostgreSQL 15
- **ORM:** SQLAlchemy 2.0+
- **Scraping:** NewsAPI (API gratuita con límite de 100 requests/día)
- **Scheduler:** APScheduler
- **Tests:** pytest

## 🔒 Seguridad

⚠️ **IMPORTANTE para Producción:**

1. Cambia `SECRET_KEY` en `.env`
2. Cambia `WTF_CSRF_SECRET_KEY` en `.env`
3. Cambia `DB_PASSWORD` en `.env` y `docker-compose.yml`
4. Habilita HTTPS/TLS
5. Nunca compartas tu `NEWSAPI_KEY`

## 📄 Licencia

Este proyecto es parte del desarrollo académico/personal.

## 🤝 Contribuciones

MVP desarrollado con Claude Code (Anthropic)

---

**🤖 WebIAScrap v0.0.0** - Mantente actualizado con las últimas noticias de IA
