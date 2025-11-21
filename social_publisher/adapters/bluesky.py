"""
Adaptador para Bluesky
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta, timezone

from .base import SocialMediaAdapter, PostContent, PostResult

logger = logging.getLogger(__name__)


class BlueskyAdapter(SocialMediaAdapter):
    """
    Adaptador para publicar en Bluesky

    Documentación: https://docs.bsky.app/

    Bluesky usa el protocolo AT (Authenticated Transfer Protocol)
    Límite: 300 caracteres por post
    """

    API_BASE_URL = "https://bsky.social/xrpc"
    MAX_POST_LENGTH = 300

    def __init__(self, credentials: Dict[str, str], config: Optional[Dict] = None):
        super().__init__(credentials, config)
        self.handle = credentials.get('handle')  # usuario.bsky.social
        self.app_password = credentials.get('app_password')
        self.did = None  # Decentralized Identifier
        self.access_jwt = None  # JWT token

    def authenticate(self) -> bool:
        """
        Autenticar con Bluesky usando App Password

        Bluesky usa un sistema de autenticación muy simple:
        1. Enviar handle + app_password
        2. Recibir JWT token y DID
        """
        try:
            if not self.handle or not self.app_password:
                logger.error("Bluesky: handle o app_password no proporcionados")
                return False

            # Crear sesión
            auth_data = {
                "identifier": self.handle,
                "password": self.app_password
            }

            response = requests.post(
                f"{self.API_BASE_URL}/com.atproto.server.createSession",
                json=auth_data,
                timeout=10
            )

            if response.status_code == 200:
                session_data = response.json()
                self.access_jwt = session_data.get('accessJwt')
                self.did = session_data.get('did')
                self._authenticated = True

                logger.info(f"Bluesky: Autenticación exitosa - {self.handle}")
                return True
            else:
                logger.error(f"Bluesky: Error de autenticación - {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Bluesky: Error en autenticación - {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verificar credenciales"""
        return self.authenticate()

    def format_content(self, content: PostContent) -> Dict:
        """
        Formatear contenido para Bluesky

        Bluesky usa formato similar a Twitter pero con 300 caracteres

        Args:
            content: Contenido a formatear

        Returns:
            Diccionario con formato de Bluesky
        """
        text_parts = []

        # Texto principal (usar descripción)
        main_text = content.descripcion

        # Hashtags (máximo 2-3)
        hashtags_to_use = content.hashtags[:3] if content.hashtags else []

        # Extraer nombre de la fuente
        source_name = self._extract_source_name(content.url) if content.url else ""
        source_part = f"\n📰 Vía: {source_name}" if source_name else ""

        # URL
        url_part = f"\n🔗 {content.url}" if content.url else ""

        # Hashtags
        hashtags_part = ""
        if hashtags_to_use:
            hashtags_part = "\n" + self._format_hashtags(hashtags_to_use)

        # Footer con disclaimer
        footer = "\n\nℹ️ Resumen automático - Crédito al original"

        # Calcular espacio disponible
        reserved_space = len(source_part) + len(url_part) + len(hashtags_part) + len(footer)
        available_for_text = self.MAX_POST_LENGTH - reserved_space - 10

        # Truncar si es necesario
        if len(main_text) > available_for_text:
            main_text = self._truncate_text(main_text, available_for_text)

        # Construir post
        post_text = main_text + source_part + url_part + hashtags_part + footer

        # Safety check
        if len(post_text) > self.MAX_POST_LENGTH:
            post_text = self._truncate_text(post_text, self.MAX_POST_LENGTH)

        # Formato AT Protocol
        # Timestamp en formato ISO 8601
        created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

        post_data = {
            "repo": self.did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": post_text,
                "createdAt": created_at
            }
        }

        return post_data

    def publish(self, content: PostContent) -> PostResult:
        """
        Publicar contenido en Bluesky

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
                        platform='bluesky',
                        error='Autenticación fallida'
                    )

            # Formatear contenido
            post_data = self.format_content(content)

            # Headers
            headers = {
                'Authorization': f'Bearer {self.access_jwt}',
                'Content-Type': 'application/json'
            }

            # Publicar usando createRecord
            response = requests.post(
                f"{self.API_BASE_URL}/com.atproto.repo.createRecord",
                json=post_data,
                headers=headers,
                timeout=30
            )

            # Procesar respuesta
            if response.status_code == 200:
                # Éxito
                response_data = response.json()
                post_uri = response_data.get('uri', 'unknown')

                # Construir URL del post
                # Formato: https://bsky.app/profile/{handle}/post/{rkey}
                # Extraer rkey del URI
                rkey = post_uri.split('/')[-1] if '/' in post_uri else 'unknown'
                post_url = f"https://bsky.app/profile/{self.handle}/post/{rkey}"

                logger.info(f"Bluesky: Post publicado exitosamente - {post_uri}")

                return PostResult(
                    success=True,
                    platform='bluesky',
                    post_id=post_uri,
                    post_url=post_url
                )
            else:
                # Error
                error_msg = response.text
                logger.error(f"Bluesky: Error al publicar - {response.status_code}: {error_msg}")

                return PostResult(
                    success=False,
                    platform='bluesky',
                    error=f"HTTP {response.status_code}: {error_msg}"
                )

        except Exception as e:
            logger.error(f"Bluesky: Excepción al publicar - {e}")
            return PostResult(
                success=False,
                platform='bluesky',
                error=str(e)
            )

    def get_rate_limit(self) -> Dict:
        """
        Obtener información de rate limiting

        Bluesky no publica límites oficiales, pero son muy generosos
        para uso personal razonable.

        Returns:
            Diccionario con estimación de límites
        """
        return {
            'limit': 1000,  # Estimado
            'remaining': 1000,
            'reset_at': datetime.utcnow() + timedelta(days=1)
        }

    def _extract_source_name(self, url: str) -> str:
        """
        Extraer nombre legible de la fuente desde la URL

        Args:
            url: URL del artículo

        Returns:
            Nombre de la fuente
        """
        if not url:
            return ""

        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc

            # Remover www. si existe
            if domain.startswith('www.'):
                domain = domain[4:]

            # Capitalizar primera letra
            # techcrunch.com -> Techcrunch.com
            parts = domain.split('.')
            if len(parts) >= 2:
                name = parts[0].capitalize()
                return f"{name}.{parts[-1]}"

            return domain.capitalize()

        except Exception:
            return ""
