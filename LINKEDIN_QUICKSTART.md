# 🚀 LinkedIn - Inicio Rápido

**Fecha:** 20 de Noviembre de 2025

---

## 📋 Resumen de Pasos

LinkedIn es **la plataforma más compleja** de configurar, pero la más valiosa para noticias profesionales de IA.

**Tiempo total estimado:** 60-90 minutos (puede tardar más por aprobaciones)

---

## ✅ Checklist de Configuración

### Fase 1: Crear LinkedIn Page (30 min)
- [ ] **1.1** Ir a: https://www.linkedin.com/company/setup/new/
- [ ] **1.2** Crear Company Page con nombre: `Schaller & Ponce AI News`
- [ ] **1.3** Completar perfil de la página (logo, banner, descripción)
- [ ] **1.4** Obtener **Page ID** desde Admin tools > Page details

### Fase 2: Crear App en Developer Portal (20 min)
- [ ] **2.1** Ir a: https://www.linkedin.com/developers/apps
- [ ] **2.2** Crear app: `WebIAScraperNewsBot`
- [ ] **2.3** Solicitar producto "Share on LinkedIn"
- [ ] **2.4** Esperar aprobación (1-7 días) ⏰

### Fase 3: Configurar OAuth 2.0 (30 min después de aprobación)
- [ ] **3.1** En tab "Auth", añadir Redirect URL: `http://localhost:8080/callback`
- [ ] **3.2** Copiar **Client ID** y **Client Secret**
- [ ] **3.3** Construir URL de autorización (ver guía)
- [ ] **3.4** Abrir en navegador y autorizar
- [ ] **3.5** Capturar `code` del callback
- [ ] **3.6** Intercambiar `code` por `access_token` con curl
- [ ] **3.7** Obtener **Person URN** con curl

### Fase 4: Configurar Proyecto (10 min)
- [ ] **4.1** Editar `.env.social_publisher`
- [ ] **4.2** Añadir credenciales LinkedIn
- [ ] **4.3** Habilitar en `ENABLED_PLATFORMS=telegram,bluesky,twitter,linkedin`
- [ ] **4.4** Rebuild contenedor: `docker-compose build social_publisher`
- [ ] **4.5** Reiniciar: `docker-compose up -d social_publisher`

### Fase 5: Probar (10 min)
- [ ] **5.1** Ver logs: `docker-compose logs -f social_publisher`
- [ ] **5.2** Añadir noticia de prueba
- [ ] **5.3** Verificar publicación en LinkedIn Page

---

## 🔑 Credenciales Necesarias

Al final del proceso necesitarás:

```bash
LINKEDIN_CLIENT_ID=tu_client_id
LINKEDIN_CLIENT_SECRET=tu_client_secret
LINKEDIN_ACCESS_TOKEN=tu_access_token
LINKEDIN_PERSON_URN=urn:li:person:abc123xyz
```

---

## ⏰ ¡IMPORTANTE! Aprobación de LinkedIn

LinkedIn debe **aprobar manualmente** tu solicitud de "Share on LinkedIn" product.

**Tiempo de espera:** 1-7 días (a veces más)

**Mientras esperas:**
- ✅ Puedes completar toda la configuración
- ✅ Obtener credenciales
- ❌ NO podrás publicar hasta que aprueben

**Email de notificación:** schaller.ponce@gmail.com

---

## 🆘 URLs de Ayuda Rápida

1. **Crear Page:** https://www.linkedin.com/company/setup/new/
2. **Developer Portal:** https://www.linkedin.com/developers/apps
3. **Documentación OAuth:** https://docs.microsoft.com/en-us/linkedin/shared/authentication/
4. **Guía Completa:** Ver `SETUP_LINKEDIN.md`

---

## 💡 Tips Clave

1. **Page vs Profile:** La API solo funciona con Company Pages, NO con perfiles personales
2. **OAuth es complejo:** Requiere flow manual con navegador y curl
3. **Tokens expiran:** A diferencia de Twitter, necesitarás renovar cada 60 días
4. **Paciencia:** La aprobación puede tardar, es normal

---

## 📞 Contacto

**Proyecto:** schaller.ponce@gmail.com

---

## ✨ Próximo Paso

👉 **Abre:** `SETUP_LINKEDIN.md` para la guía paso a paso completa

👉 **Empieza por:** Crear la LinkedIn Company Page

---

**Última actualización:** 20 de Noviembre de 2025
