# 📖 Manual del Usuario - WebIAScrap v0.0.0

## Tabla de Contenidos

1. [Introducción](#introducción)
2. [Primeros Pasos](#primeros-pasos)
3. [Uso de la Aplicación](#uso-de-la-aplicación)
4. [Preguntas Frecuentes](#preguntas-frecuentes)
5. [Solución de Problemas](#solución-de-problemas)

---

## Introducción

### ¿Qué es WebIAScrap?

WebIAScrap es una aplicación que te ayuda a mantenerte actualizado sobre las últimas noticias de Inteligencia Artificial, Machine Learning y Ciencia de Datos. La aplicación:

- Busca automáticamente noticias de fuentes confiables
- Te muestra las 30 noticias más recientes
- Te permite seleccionar las que te interesan
- Guarda tus selecciones para procesamiento posterior

### Características Principales

✅ **Interfaz oscura:** Diseñada en tonos azules oscuros para reducir la fatiga ocular
✅ **Actualización automática:** Obtiene nuevas noticias cada 24 horas
✅ **Búsqueda inteligente:** Extrae automáticamente temas relevantes de cada noticia
✅ **Selección fácil:** Marca las noticias que te interesan con un simple click

---

## Primeros Pasos

### Requisitos

Para usar WebIAScrap necesitas:

1. **Computadora con Docker instalado**
   - Windows: Docker Desktop
   - Mac: Docker Desktop
   - Linux: Docker + Docker Compose

2. **Cuenta gratuita en NewsAPI**
   - Ve a https://newsapi.org/register
   - Regístrate (es gratis)
   - Copia tu API key

3. **Conexión a Internet**

### Instalación

#### Paso 1: Obtener tu API Key

1. Abre tu navegador y ve a https://newsapi.org/register
2. Completa el formulario de registro
3. Verifica tu email
4. Inicia sesión y copia tu API Key (aparece en tu dashboard)

#### Paso 2: Configurar la Aplicación

1. Abre una terminal/consola
2. Navega al directorio del proyecto:
   ```bash
   cd ~/Projects/webiascrap_v0.0.0
   ```

3. Edita el archivo `.env`:
   ```bash
   nano .env
   ```
   o usa cualquier editor de texto

4. Encuentra esta línea:
   ```
   NEWSAPI_KEY=your-newsapi-key-here
   ```

5. Reemplázala con tu API key real:
   ```
   NEWSAPI_KEY=abc123xyz456tuapikey
   ```

6. Guarda el archivo (Ctrl+X, luego Y, luego Enter en nano)

#### Paso 3: Iniciar la Aplicación

1. En la terminal, ejecuta:
   ```bash
   docker-compose up --build
   ```

2. Espera a que aparezcan mensajes como:
   ```
   webiascrap_db     | database system is ready to accept connections
   webiascrap_app    | 🚀 Iniciando WebIAScrap...
   ```

3. Abre tu navegador en: **http://localhost:8000**

¡Listo! La aplicación está funcionando.

---

## Uso de la Aplicación

### Interfaz Principal

Al abrir la aplicación verás:

```
┌─────────────────────────────────────────┐
│ 🤖 WebIAScrap                          │
│                                         │
│ [📰 Noticias] [📤 A Publicar] [🔄]     │
└─────────────────────────────────────────┘

📰 Últimas Noticias de IA

┌─────────────────────────────────────────┐
│ 30                                      │
│ Noticias Disponibles                    │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ ☐ AI Breakthrough in Neural Networks   │
│   📅 17/11/2024 14:30                  │
│   🏷️ AI, Neural Network, Deep Learning │
│                                         │
│   Researchers have discovered...        │
│                                         │
│   🔗 Leer artículo completo →          │
└─────────────────────────────────────────┘

...más noticias...

┌─────────────────────────────────────────┐
│ ☐ Seleccionar todo                     │
│         [📤 Copiar seleccionadas]      │
└─────────────────────────────────────────┘
```

### Navegación

#### Menú Superior

- **📰 Noticias:** Lista principal de noticias (página de inicio)
- **📤 A Publicar:** Noticias que has seleccionado
- **🔄 Actualizar Noticias:** Obtener nuevas noticias inmediatamente

### Cómo Leer Noticias

1. **Ver lista de noticias:**
   - La página principal muestra las 30 noticias más recientes
   - Ordenadas de más reciente a más antigua

2. **Información de cada noticia:**
   - **Título:** Clickeable, abre el artículo completo en nueva pestaña
   - **Fecha:** Cuándo fue publicada la noticia
   - **Temas:** Palabras clave extraídas automáticamente
   - **Resumen:** Primeras 300 palabras del artículo

3. **Leer artículo completo:**
   - Click en el título O en "🔗 Leer artículo completo →"
   - Se abre en una nueva pestaña del navegador

### Cómo Seleccionar Noticias

#### Seleccionar Individual

1. Click en el checkbox ☐ al lado de cada noticia
2. El checkbox se marca ☑
3. Click nuevamente para desmarcar

#### Seleccionar Todas

1. Click en "☐ Seleccionar todo" en la parte inferior
2. Todas las noticias se marcarán ☑
3. Click nuevamente para desmarcar todas

#### Guardar Selección

1. Marca las noticias que te interesan ☑
2. Click en el botón **"📤 Copiar seleccionadas a 'A Publicar'"**
3. Verás un mensaje de confirmación: "✅ X noticia(s) copiada(s)"
4. Las noticias seleccionadas ahora están en "A Publicar"

### Ver Noticias Seleccionadas

1. Click en **"📤 A Publicar"** en el menú superior
2. Verás todas las noticias que has marcado como interesantes
3. Incluye información de cuándo la seleccionaste

### Actualizar Noticias Manualmente

1. Click en **"🔄 Actualizar Noticias"** en el menú
2. La aplicación buscará nuevas noticias inmediatamente
3. Espera unos segundos
4. Verás las nuevas noticias en la lista

---

## Preguntas Frecuentes

### ¿Cada cuánto se actualizan las noticias automáticamente?

Cada 24 horas. También puedes actualizar manualmente cuando quieras.

### ¿Cuántas noticias se guardan?

La aplicación mantiene las 30 noticias más recientes. Las más antiguas se eliminan automáticamente.

### ¿De dónde vienen las noticias?

Por defecto de:
- TechCrunch
- Wired
- The Verge
- Ars Technica

Puedes cambiar las fuentes en la configuración (archivo `.env`).

### ¿Qué pasa con las noticias que selecciono?

Se copian a una tabla especial llamada "APublicar". En la versión 0.1.0 se procesarán automáticamente para publicación.

### ¿Puedo cambiar los colores de la interfaz?

Los colores están optimizados para reducir fatiga ocular. Si quieres cambiarlos, puedes editar el archivo `src/static/css/style.css`.

### ¿La aplicación funciona sin internet?

No. Necesita internet para obtener noticias de NewsAPI.

### ¿Cuánto cuesta NewsAPI?

La versión gratuita permite 100 búsquedas por día, más que suficiente para esta aplicación.

---

## Solución de Problemas

### La aplicación no muestra noticias

**Problema:** Página vacía o mensaje "No hay noticias disponibles"

**Soluciones:**

1. Verifica que configuraste tu API key correctamente:
   ```bash
   cat .env | grep NEWSAPI_KEY
   ```
   Debe mostrar tu API key, no "your-newsapi-key-here"

2. Verifica que tu API key sea válida:
   - Ve a https://newsapi.org/account
   - Revisa tu API key

3. Prueba actualizar manualmente:
   - Click en "🔄 Actualizar Noticias"

4. Revisa los logs:
   ```bash
   docker-compose logs app
   ```

### Error "Database connection failed"

**Problema:** La aplicación no puede conectarse a la base de datos

**Soluciones:**

1. Espera 10-15 segundos después de iniciar Docker
2. Reinicia los contenedores:
   ```bash
   docker-compose restart
   ```

3. Si persiste, reinicia completamente:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### La página no carga (Error 404 o 500)

**Problema:** El navegador no puede cargar la página

**Soluciones:**

1. Verifica que Docker esté ejecutándose:
   ```bash
   docker-compose ps
   ```
   Ambos servicios (app y db) deben estar "Up"

2. Verifica que estás usando el puerto correcto:
   - Debe ser: http://localhost:8000
   - No: http://localhost:80 o http://localhost:5000

3. Revisa los logs:
   ```bash
   docker-compose logs app
   ```

### Los checkboxes no funcionan

**Problema:** No puedes marcar/desmarcar noticias

**Soluciones:**

1. Refresca la página (F5)
2. Limpia caché del navegador (Ctrl+Shift+Delete)
3. Prueba en modo incógnito
4. Prueba otro navegador (Chrome, Firefox, Edge)

### El botón "Copiar seleccionadas" no hace nada

**Problema:** Click en el botón pero no pasa nada

**Soluciones:**

1. Verifica que hayas seleccionado al menos una noticia (☑)
2. Refresca la página
3. Revisa los logs para errores:
   ```bash
   docker-compose logs app
   ```

### Cómo detener la aplicación

```bash
docker-compose down
```

### Cómo reiniciar desde cero

```bash
# Detener y eliminar todo (incluyendo base de datos)
docker-compose down -v

# Iniciar de nuevo
docker-compose up --build
```

⚠️ **Advertencia:** Esto eliminará todas las noticias guardadas.

---

## Contacto y Soporte

Para reportar problemas o sugerencias:
1. Revisa este manual
2. Revisa el README.md del proyecto
3. Revisa los logs: `docker-compose logs`

---

**🤖 WebIAScrap v0.0.0** - Manual del Usuario
*Actualizado: Noviembre 2024*
