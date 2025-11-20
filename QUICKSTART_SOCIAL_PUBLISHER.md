# ⚡ Quick Start: SocialPublisher

Guía rápida para poner en marcha la publicación automatizada en redes sociales en menos de 30 minutos.

---

## 🎯 Prerrequisitos

Antes de comenzar, asegúrate de tener:

- ✅ WebIAScraper funcionando (`docker-compose up`)
- ✅ Cuentas creadas en las plataformas que quieras usar (LinkedIn, Twitter, Bluesky, Telegram)
- ✅ 30 minutos de tiempo

---

## 🚀 Pasos Rápidos

### 1. Migrar Base de Datos (2 minutos)

```bash
cd ~/Projects/webiascrap_v0.0.0

# Ejecutar migración
./migrate_db.sh

# Responde "s" cuando te pregunte
```

**Resultado esperado:**
```
✅ Migración completada exitosamente
```

---

### 2. Configurar Credenciales (20-25 minutos)

#### 2.1 Crear archivo de configuración

```bash
cp .env.social_publisher.example .env.social_publisher
nano .env.social_publisher
```

#### 2.2 Completar credenciales

Para **testing rápido**, empieza solo con **Telegram** (el más fácil):

##### Telegram (5 minutos)

1. Abre Telegram y busca `@BotFather`
2. Envía `/newbot` y sigue instrucciones
3. Copia el **Bot Token**
4. Crea un canal nuevo (público o privado)
5. Añade el bot como administrador del canal
6. En `.env.social_publisher`:

```bash
ENABLED_PLATFORMS=telegram

TELEGRAM_BOT_TOKEN=123456789:ABCdef...  # El token del BotFather
TELEGRAM_CHANNEL_ID=@tu_canal           # Para público, o -100xxx para privado
```

**Para añadir más plataformas**, consulta [SETUP_SOCIAL_MEDIA.md](SETUP_SOCIAL_MEDIA.md).

---

### 3. Iniciar Servicios (2 minutos)

```bash
# Build y start
docker-compose up --build -d

# Ver logs de SocialPublisher
docker-compose logs -f social_publisher
```

**Logs esperados:**
```
✅ Telegram: Adaptador inicializado
✅ Plataformas configuradas: telegram
🔄 Iniciando loop de polling...
```

---

### 4. Test Manual (5 minutos)

#### 4.1 Preparar una noticia

1. Abre WebIAScraper: http://localhost:8000
2. Si no hay noticias, click en "🔄 Actualizar Noticias"
3. Selecciona una noticia (checkbox)
4. Click "Copiar a 'A Publicar'"

#### 4.2 Procesar la noticia

1. Ve a la sección "A Publicar" (menú superior)
2. Click en "Procesar" en la noticia
3. Espera ~10 segundos (traduce y optimiza con Claude)
4. Verifica que aparece ✅ en "Procesado"

#### 4.3 Ver la publicación

**Opción A: Esperar polling automático**
- Espera 5 minutos (intervalo por defecto)
- El servicio publicará automáticamente

**Opción B: Forzar publicación**
```bash
# Reiniciar servicio para forzar ciclo inmediato
docker-compose restart social_publisher

# Ver logs
docker-compose logs -f social_publisher
```

#### 4.4 Verificar

1. **En Telegram:** Ve a tu canal, debería aparecer la noticia
2. **En logs:**
   ```
   📤 Publicando noticia X en telegram...
   ✅ telegram: Publicación exitosa
   ```
3. **En Base de Datos:**
   ```bash
   docker-compose exec db psql -U webiauser -d webiascrap \
     -c "SELECT titulo_es, publicado FROM apublicar LIMIT 1;"
   ```

---

## ✅ Verificación de Éxito

Si todo funcionó correctamente:

- ✅ Noticia aparece en tu canal de Telegram
- ✅ Logs muestran "Publicación exitosa"
- ✅ En BD: `publicado = true`
- ✅ No hay errores en logs

---

## 🔧 Añadir Más Plataformas

Una vez que Telegram funcione, puedes añadir más plataformas:

### LinkedIn (15 minutos)

Ver guía completa en [SETUP_SOCIAL_MEDIA.md#2-linkedin](SETUP_SOCIAL_MEDIA.md#2-linkedin)

### Twitter/X (10 minutos)

Ver guía completa en [SETUP_SOCIAL_MEDIA.md#3-twitterx](SETUP_SOCIAL_MEDIA.md#3-twitterx)

### Bluesky (5 minutos)

Ver guía completa en [SETUP_SOCIAL_MEDIA.md#4-bluesky](SETUP_SOCIAL_MEDIA.md#4-bluesky)

---

## 📊 Configuración Común

### Cambiar Intervalo de Polling

En `.env.social_publisher`:

```bash
# Cada 5 minutos (default)
POLL_INTERVAL_SECONDS=300

# Cada hora
POLL_INTERVAL_SECONDS=3600

# Cada 10 minutos
POLL_INTERVAL_SECONDS=600
```

Reinicia el servicio:
```bash
docker-compose restart social_publisher
```

### Habilitar/Deshabilitar Plataformas

En `.env.social_publisher`:

```bash
# Solo Telegram
ENABLED_PLATFORMS=telegram

# Telegram y Twitter
ENABLED_PLATFORMS=telegram,twitter

# Todas
ENABLED_PLATFORMS=linkedin,twitter,bluesky,telegram
```

---

## 🐛 Troubleshooting Rápido

### Error: "No hay adaptadores disponibles"

**Causa:** Credenciales incorrectas o faltantes.

**Solución:**
```bash
# Verificar archivo existe
ls -la .env.social_publisher

# Ver logs específicos
docker-compose logs social_publisher | grep -i error

# Verificar credenciales
cat .env.social_publisher | grep TELEGRAM_BOT_TOKEN
```

### Error: "Autenticación fallida"

**Para Telegram:**
- Verifica que el Bot Token es correcto
- Verifica que el bot es admin del canal

**Para otras plataformas:**
- Consulta [SETUP_SOCIAL_MEDIA.md](SETUP_SOCIAL_MEDIA.md) para detalles

### Las noticias no se publican

**Checklist:**
1. ¿La noticia está procesada? (debe tener `procesado = true`)
2. ¿El servicio está corriendo? (`docker-compose ps`)
3. ¿Hay errores en logs? (`docker-compose logs social_publisher`)
4. ¿Pasaron 5 minutos desde el último ciclo?

---

## 📚 Recursos

- 📖 [Guía Completa de Configuración](SETUP_SOCIAL_MEDIA.md)
- 📖 [Documentación del SocialPublisher](social_publisher/README.md)
- 📊 [Informe de Factibilidad](SOCIAL_MEDIA_FEASIBILITY_REPORT.md)
- 📝 [Resumen de Implementación](FASE1_IMPLEMENTATION_SUMMARY.md)

---

## 🎉 ¡Listo!

Si llegaste hasta aquí y todo funcionó, ¡felicitaciones! 🎊

Tu sistema ahora:
- ✅ Scrapea noticias de IA automáticamente
- ✅ Te permite seleccionar las interesantes
- ✅ Las procesa y optimiza para RRSS
- ✅ Las publica automáticamente

**Siguiente paso:** Monitorea los logs durante unos días y ajusta según necesites.

---

**Tiempo total estimado:** 30 minutos
**Dificultad:** Media
**Resultado:** Sistema completamente automatizado

**¿Problemas?** Consulta [SETUP_SOCIAL_MEDIA.md](SETUP_SOCIAL_MEDIA.md) o revisa logs detallados.
