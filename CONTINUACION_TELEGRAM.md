# 📋 Continuación: Configuración de Redes Sociales

**Fecha:** 19 de Noviembre de 2025
**Estado:** Telegram configurado y testeado ✅

---

## ✅ Lo que completamos hoy

### 1. Telegram - COMPLETADO
- ✅ **Bot creado:** `@WebIAScrapperBot`
- ✅ **Bot Token:** Configurado en `.env.social_publisher` (línea 61)
- ✅ **Canal:** "Schaller&Ponce AI" (`@schallerponce`)
- ✅ **Channel ID:** `-1003454134750` (configurado en línea 62)
- ✅ **Permisos:** Bot añadido como administrador con permisos de publicación
- ✅ **Test:** Mensaje de prueba enviado exitosamente
- ✅ **Commit:** Todo guardado en git (commit: 3c6d292)

### 2. Archivos de Configuración
```bash
~/Projects/webiascrap_v0.0.0/.env.social_publisher
```

**Configuración actual:**
```bash
ENABLED_PLATFORMS=telegram
TELEGRAM_BOT_TOKEN=8373359883:AAF41sFLMJDMVVodAKYEQ_jwezrDPimUlo0
TELEGRAM_CHANNEL_ID=-1003454134750
```

**⚠️ IMPORTANTE:** El archivo `.env.social_publisher` contiene credenciales sensibles y está protegido en `.gitignore`.

---

## 📝 Próximos pasos para mañana

### Opción A: Probar el Sistema Completo con Telegram

1. **Migrar la base de datos** (si no está hecha):
   ```bash
   cd ~/Projects/webiascrap_v0.0.0
   ./migrate_db.sh
   ```

2. **Levantar los servicios:**
   ```bash
   docker-compose down
   docker-compose build
   docker-compose up -d
   ```

3. **Verificar que todo funciona:**
   ```bash
   # Ver logs del social publisher
   docker-compose logs -f social_publisher

   # Deberías ver:
   # ✅ Telegram: Adaptador inicializado
   # 🔄 Iniciando loop de polling...
   ```

4. **Crear una noticia de prueba:**
   - Abrir http://localhost:8000
   - Buscar noticias de IA
   - Seleccionar una noticia interesante
   - Click en "Copiar a 'A Publicar'"
   - En la tabla "A Publicar", click en "Procesar"
   - Esperar ~5 minutos o reiniciar: `docker-compose restart social_publisher`
   - Verificar en tu canal de Telegram: https://t.me/schallerponce

5. **Verificar en la base de datos:**
   ```bash
   docker-compose exec db psql -U webiauser -d webiascrap

   # Ver noticias publicadas
   SELECT id, titulo_es, publicado, plataformas_publicadas
   FROM apublicar
   WHERE publicado = true;
   ```

### Opción B: Configurar Más Redes Sociales

Puedes configurar cualquiera de estas plataformas siguiendo la guía:

#### 1. **Bluesky** (La más fácil)
   - **Tiempo estimado:** 10 minutos
   - **Pasos:** Ver `SETUP_SOCIAL_MEDIA.md` sección 4
   - Crear cuenta en https://bsky.app/
   - Generar App Password
   - Configurar en `.env.social_publisher`

#### 2. **Twitter/X**
   - **Tiempo estimado:** 20-30 minutos
   - **Pasos:** Ver `SETUP_SOCIAL_MEDIA.md` sección 3
   - Crear Developer Account
   - Generar API Keys
   - Configurar permisos Read & Write

#### 3. **LinkedIn**
   - **Tiempo estimado:** 30-40 minutos (más complejo)
   - **Pasos:** Ver `SETUP_SOCIAL_MEDIA.md` sección 2
   - Crear LinkedIn App
   - OAuth 2.0 flow
   - Obtener Access Token

### Opción C: Revisar y Personalizar

1. **Personalizar formatos de mensaje:**
   - Editar `social_publisher/adapters/telegram.py`
   - Modificar el método `_format_message()`
   - Añadir emojis, hashtags personalizados, etc.

2. **Ajustar configuración de polling:**
   ```bash
   nano .env.social_publisher

   # Cambiar:
   POLL_INTERVAL_SECONDS=300  # 5 minutos (puedes reducir para testing)
   MAX_NEWS_PER_CYCLE=5       # Noticias por ciclo
   ```

3. **Revisar logs y monitoreo:**
   ```bash
   # Logs en tiempo real
   docker-compose logs -f social_publisher

   # Ver solo errores
   docker-compose logs social_publisher | grep ERROR
   ```

---

## 📚 Documentación Disponible

Toda la documentación está en tu proyecto:

1. **`SETUP_SOCIAL_MEDIA.md`** - Guía paso a paso para configurar TODAS las redes
2. **`QUICKSTART_SOCIAL_PUBLISHER.md`** - Inicio rápido del sistema
3. **`social_publisher/README.md`** - Documentación técnica del microservicio
4. **`FASE1_IMPLEMENTATION_SUMMARY.md`** - Resumen de lo implementado

---

## 🔧 Comandos Útiles

```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs
docker-compose logs -f social_publisher

# Reiniciar solo el publisher
docker-compose restart social_publisher

# Rebuild completo
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Conectar a la base de datos
docker-compose exec db psql -U webiauser -d webiascrap

# Ver variables de entorno del publisher
docker-compose exec social_publisher env | grep TELEGRAM
```

---

## 🎯 Recordatorios Importantes

1. **Credenciales Seguras:**
   - NUNCA commitear `.env.social_publisher` (ya está en `.gitignore`)
   - El Bot Token está en línea 61 del archivo
   - El archivo `WebIAScrapperBot Token.txt` tampoco debe commitearse

2. **Base de Datos:**
   - Asegurarse de ejecutar `migrate_db.sh` antes de usar el publisher
   - Las nuevas columnas son: `publicado`, `plataformas_publicadas`, `intentos_publicacion`, `ultimo_error`, `published_at`

3. **Telegram Bot:**
   - El bot debe permanecer como administrador del canal
   - Si cambias el nombre del canal, actualiza el `TELEGRAM_CHANNEL_ID`
   - Puedes verificar el bot en: https://t.me/BotFather

4. **Flujo Completo:**
   ```
   NewsAPI → WebIAScraper → Usuario selecciona → "A Publicar"
   → Usuario procesa con Claude → SocialPublisher automático → Telegram
   ```

---

## 🐛 Troubleshooting

### Si el bot no publica:

1. **Verificar logs:**
   ```bash
   docker-compose logs social_publisher
   ```

2. **Verificar que el bot es admin:**
   - Abrir canal en Telegram
   - Verificar que `@WebIAScrapperBot` está en Administrators

3. **Verificar configuración:**
   ```bash
   cat .env.social_publisher | grep TELEGRAM
   ```

4. **Test manual del bot:**
   ```bash
   curl -X POST "https://api.telegram.org/bot8373359883:AAF41sFLMJDMVVodAKYEQ_jwezrDPimUlo0/sendMessage" \
     -H "Content-Type: application/json" \
     -d '{"chat_id": "-1003454134750", "text": "Test manual"}'
   ```

5. **Verificar conectividad entre contenedores:**
   ```bash
   docker-compose exec social_publisher ping app
   ```

---

## 📞 Recursos de Ayuda

- **Telegram Bot API:** https://core.telegram.org/bots/api
- **BotFather:** https://t.me/BotFather
- **Tu Canal:** https://t.me/schallerponce
- **LinkedIn Developers:** https://www.linkedin.com/developers/
- **Twitter Developer:** https://developer.x.com/
- **Bluesky:** https://bsky.app/

---

**¡Todo listo para continuar mañana!** 🚀

El sistema de Telegram está 100% funcional. Solo falta:
1. Probar el flujo completo end-to-end, O
2. Configurar las otras plataformas (LinkedIn, Twitter, Bluesky)

Cualquier opción que elijas, toda la documentación y código está listo.
