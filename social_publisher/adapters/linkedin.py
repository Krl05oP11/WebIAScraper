"""
Adaptador para LinkedIn
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from .base import SocialMediaAdapter, PostContent, PostResult

logger = logging.getLogger(__name__)


class LinkedInAdapter(SocialMediaAdapter):
    """
    Adaptador para publicar en LinkedIn

    Documentación: https://learn.microsoft.com/en-us/linkedin/

    Rate limits: ~100 posts/día por usuario
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
        """
        try:
            if not self.access_token:
                logger.error("LinkedIn: access_token no proporcionado")
                return False

            # Verificar token obteniendo información del usuario
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            response = requests.get(
                f"{self.API_BASE_URL}/me",
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                self._authenticated = True
                logger.info("LinkedIn: Autenticación exitosa")
                return True
            else:
                logger.error(f"LinkedIn: Error de autenticación - {response.status_code}")
                return False

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

        # Hashtags
        if content.hashtags:
            hashtags_str = self._format_hashtags(content.hashtags)
            text_parts.append(f"\n\n{hashtags_str}")

        # URL (LinkedIn hace preview automático)
        if content.url:
            text_parts.append(f"\n\n🔗 {content.url}")

        # Unir todo
        full_text = "\n".join(text_parts)

        # Truncar si es necesario
        if len(full_text) > self.MAX_POST_LENGTH:
            full_text = self._truncate_text(full_text, self.MAX_POST_LENGTH)

        # Formato UGC Post
        # Documentación: https://learn.microsoft.com/en-us/linkedin/marketing/integrations/community-management/shares/ugc-post-api
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

            # Headers
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }

            # Publicar
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
