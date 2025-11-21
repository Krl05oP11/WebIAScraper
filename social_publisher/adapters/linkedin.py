"""
Adaptador para LinkedIn

⚠️ ESTADO: TEMPORALMENTE DESHABILITADO
==================================================

PROBLEMA CONOCIDO:
------------------
LinkedIn API rechaza publicaciones con error 403 ACCESS_DENIED en campo /author
a pesar de tener OAuth configurado correctamente con scope w_member_social.

Error recibido:
{
  "status": 403,
  "serviceErrorCode": 100,
  "code": "ACCESS_DENIED",
  "message": "Field Value validation failed in REQUEST_BODY:
              Data Processing Exception while processing fields [/author]"
}

CAUSA RAÍZ:
-----------
El scope w_member_social (proporcionado por producto "Share on LinkedIn") es
insuficiente para validar el campo author. Se requieren scopes adicionales que:
- Fueron deprecados (r_liteprofile, r_basicprofile)
- O requieren productos Enterprise (Community Management API)

SOLUCIÓN TEMPORAL:
------------------
Posts manuales en LinkedIn hasta obtener aprobación de productos adicionales.

SOLUCIÓN DEFINITIVA REQUERIDA:
-------------------------------
1. Contactar LinkedIn Support con reporte técnico (ver docs/LINKEDIN_ISSUE_REPORT.md)
2. Solicitar producto Community Management API cuando se formalice el negocio
3. O esperar respuesta de LinkedIn sobre configuración correcta

DOCUMENTACIÓN:
--------------
- Reporte técnico completo: docs/LINKEDIN_ISSUE_REPORT.md
- Documentación oficial: https://learn.microsoft.com/en-us/linkedin/
- Stack Overflow refs en reporte

Última actualización: 2025-11-21
==================================================
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from .base import SocialMediaAdapter, PostContent, PostResult

logger = logging.getLogger(__name__)


class LinkedInAdapter(SocialMediaAdapter):
    """
    Adaptador para publicar en LinkedIn (CÓDIGO CONSERVADO PARA FUTURO)

    Documentación: https://learn.microsoft.com/en-us/linkedin/

    Rate limits: ~100 posts/día por usuario

    NOTA: Ver header del archivo para detalles sobre estado actual y problema conocido.
    """

    API_BASE_URL = "https://api.linkedin.com/v2"
    MAX_POST_LENGTH = 3000  # LinkedIn permite hasta 3000 caracteres

    def __init__(self, credentials: Dict[str, str], config: Optional[Dict] = None):
        super().__init__(credentials, config)
        self.access_token = credentials.get('access_token')
        self.person_urn = credentials.get('person_urn')  # urn:li:person:xxxxx
        self._rate_limit_info = {
            'limit': 100,
            'remaining': 100,
            'reset_at': datetime.utcnow() + timedelta(days=1)
        }

    def authenticate(self) -> bool:
        """
        Verificar autenticación con LinkedIn

        LinkedIn usa OAuth 2.0. El access_token debe obtenerse previamente
        a través del flujo de autorización.

        Nota: Con scope w_member_social, no podemos verificar con /v2/me
        así que simplemente verificamos que el token existe.
        """
        try:
            if not self.access_token:
                logger.error("LinkedIn: access_token no proporcionado")
                return False

            if not self.person_urn:
                logger.error("LinkedIn: person_urn no proporcionado")
                return False

            # Con w_member_social, asumimos que el token es válido
            # Se verificará realmente en el primer post
            self._authenticated = True
            logger.info("LinkedIn: Credenciales configuradas correctamente")
            return True

        except Exception as e:
            logger.error(f"LinkedIn: Error en autenticación - {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verificar credenciales"""
        return self.authenticate()

    def format_content(self, content: PostContent) -> Dict:
        """
        Formatear contenido para LinkedIn UGC Posts API

        Args:
            content: Contenido a formatear

        Returns:
            Diccionario con formato de LinkedIn
        """
        # Construir texto del post
        text_parts = []

        # Título (opcional, como encabezado)
        if content.titulo:
            text_parts.append(f"📰 {content.titulo}\n")

        # Descripción/resumen
        if content.descripcion:
            text_parts.append(content.descripcion)

        # Fuente y URL con atribución clara
        if content.url:
            source_name = self._extract_source_name(content.url)
            text_parts.append(f"\n\n📰 Fuente: {source_name}")
            text_parts.append(f"🔗 Leer artículo original completo: {content.url}")

        # Hashtags
        if content.hashtags:
            hashtags_str = self._format_hashtags(content.hashtags)
            text_parts.append(f"\n\n{hashtags_str}")

        # Disclaimer y firma
        text_parts.append("\n\n📡 Schaller & Ponce AI News")
        text_parts.append("ℹ️ Resumen automático - Todo el crédito al medio original")

        # Unir todo
        full_text = "\n".join(text_parts)

        # Truncar si es necesario
        if len(full_text) > self.MAX_POST_LENGTH:
            full_text = self._truncate_text(full_text, self.MAX_POST_LENGTH)

        # Formato UGC Post (API Legacy)
        # Documentación: https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/ugc-post-api
        # IMPORTANTE: author debe ser urn:li:member:{id} NO urn:li:person:{id}
        post_data = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": full_text
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }

        return post_data

    def publish(self, content: PostContent) -> PostResult:
        """
        Publicar contenido en LinkedIn

        Args:
            content: Contenido a publicar

        Returns:
            Resultado de la publicación
        """
        try:
            if not self._authenticated:
                if not self.authenticate():
                    return PostResult(
                        success=False,
                        platform='linkedin',
                        error='Autenticación fallida'
                    )

            # Formatear contenido
            post_data = self.format_content(content)

            # Headers (UGC Posts API)
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Publicar (API Legacy /v2/ugcPosts)
            response = requests.post(
                f"{self.API_BASE_URL}/ugcPosts",
                json=post_data,
                headers=headers,
                timeout=30
            )

            # Procesar respuesta
            if response.status_code == 201:
                # Éxito
                response_data = response.headers
                post_id = response_data.get('X-RestLi-Id', 'unknown')

                # LinkedIn no devuelve URL directa, construirla
                # Formato: https://www.linkedin.com/feed/update/urn:li:ugcPost:{id}
                post_url = f"https://www.linkedin.com/feed/update/{post_id}"

                logger.info(f"LinkedIn: Publicación exitosa - {post_id}")

                return PostResult(
                    success=True,
                    platform='linkedin',
                    post_id=post_id,
                    post_url=post_url
                )
            else:
                # Error
                error_msg = response.text
                logger.error(f"LinkedIn: Error al publicar - {response.status_code}: {error_msg}")

                return PostResult(
                    success=False,
                    platform='linkedin',
                    error=f"HTTP {response.status_code}: {error_msg}"
                )

        except Exception as e:
            logger.error(f"LinkedIn: Excepción al publicar - {e}")
            return PostResult(
                success=False,
                platform='linkedin',
                error=str(e)
            )

    def get_rate_limit(self) -> Dict:
        """
        Obtener información de rate limiting

        LinkedIn no expone públicamente los límites exactos,
        pero se estima ~100 posts/día.

        Returns:
            Diccionario con estimación de límites
        """
        return self._rate_limit_info

    def _extract_source_name(self, url: str) -> str:
        """
        Extraer nombre legible de la fuente desde la URL

        Args:
            url: URL del artículo

        Returns:
            Nombre de la fuente
        """
        if not url:
            return "Fuente desconocida"

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            # Remover www. si existe
            if domain.startswith('www.'):
                domain = domain[4:]

            # Capitalizar primera letra de cada palabra
            # techcrunch.com -> TechCrunch.com
            parts = domain.split('.')
            if len(parts) >= 2:
                name = parts[0].capitalize()
                return f"{name}.{parts[-1]}"

            return domain.capitalize()

        except Exception:
            return "Fuente externa"
