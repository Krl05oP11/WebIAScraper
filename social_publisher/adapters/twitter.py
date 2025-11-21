"""
Adaptador para Twitter/X
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1Session

from .base import SocialMediaAdapter, PostContent, PostResult

logger = logging.getLogger(__name__)


class TwitterAdapter(SocialMediaAdapter):
    """
    Adaptador para publicar en Twitter/X

    Documentación: https://developer.x.com/en/docs/twitter-api

    Rate limits (Free tier): 1,500 tweets/mes
    """

    API_BASE_URL = "https://api.twitter.com/2"
    MAX_TWEET_LENGTH = 280

    def __init__(self, credentials: Dict[str, str], config: Optional[Dict] = None):
        super().__init__(credentials, config)
        self.api_key = credentials.get('api_key')
        self.api_secret = credentials.get('api_secret')
        self.access_token = credentials.get('access_token')
        self.access_token_secret = credentials.get('access_token_secret')
        self.bearer_token = credentials.get('bearer_token')

        self._rate_limit_info = {
            'limit': 1500,  # tweets/mes en free tier
            'remaining': 1500,
            'reset_at': datetime.utcnow() + timedelta(days=30)
        }

    def authenticate(self) -> bool:
        """
        Verificar autenticación con Twitter

        Twitter API v2 usa OAuth 1.0a para posting con tokens que no expiran
        """
        try:
            # Verificar que tenemos todas las credenciales OAuth 1.0a
            if not all([self.api_key, self.api_secret, self.access_token, self.access_token_secret]):
                logger.error("Twitter: Credenciales OAuth 1.0a incompletas")
                return False

            # Crear sesión OAuth 1.0a
            oauth = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )

            # Verificar autenticación obteniendo información del usuario
            response = oauth.get(
                f"{self.API_BASE_URL}/users/me",
                timeout=10
            )

            if response.status_code == 200:
                self._authenticated = True
                user_data = response.json()
                logger.info(f"Twitter: Autenticación exitosa - @{user_data.get('data', {}).get('username', 'unknown')}")
                return True
            else:
                logger.error(f"Twitter: Error de autenticación - {response.status_code}: {response.text}")
                return False

        except Exception as e:
            logger.error(f"Twitter: Error en autenticación - {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verificar credenciales"""
        return self.authenticate()

    def format_content(self, content: PostContent) -> Dict:
        """
        Formatear contenido para Twitter

        Twitter tiene límite de 280 caracteres, así que necesitamos
        ser muy concisos.

        Args:
            content: Contenido a formatear

        Returns:
            Diccionario con formato de Twitter
        """
        text_parts = []

        # Usar resumen corto si está disponible en el contenido original
        # Si no, usar descripción truncada
        main_text = content.descripcion

        # Hashtags (máximo 2-3 para no saturar)
        hashtags_to_use = content.hashtags[:3] if content.hashtags else []

        # URL
        url_part = f" {content.url}" if content.url else ""

        # Hashtags
        hashtags_part = ""
        if hashtags_to_use:
            hashtags_part = " " + self._format_hashtags(hashtags_to_use)

        # Calcular espacio disponible
        # Estructura: [texto principal] [URL] [hashtags]
        reserved_space = len(url_part) + len(hashtags_part)
        available_for_text = self.MAX_TWEET_LENGTH - reserved_space - 5  # 5 chars de margen

        # Truncar texto principal si es necesario
        if len(main_text) > available_for_text:
            main_text = self._truncate_text(main_text, available_for_text, suffix="...")

        # Construir tweet
        tweet_text = main_text + url_part + hashtags_part

        # Asegurar que no exceda el límite (safety check)
        if len(tweet_text) > self.MAX_TWEET_LENGTH:
            tweet_text = self._truncate_text(tweet_text, self.MAX_TWEET_LENGTH)

        return {
            "text": tweet_text
        }

    def publish(self, content: PostContent) -> PostResult:
        """
        Publicar contenido en Twitter

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
                        platform='twitter',
                        error='Autenticación fallida'
                    )

            # Formatear contenido
            tweet_data = self.format_content(content)

            # Crear sesión OAuth 1.0a
            oauth = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.access_token,
                resource_owner_secret=self.access_token_secret
            )

            # Publicar usando OAuth 1.0a
            response = oauth.post(
                f"{self.API_BASE_URL}/tweets",
                json=tweet_data,
                timeout=30
            )

            # Procesar respuesta
            if response.status_code == 201:
                # Éxito
                response_data = response.json()
                tweet_id = response_data.get('data', {}).get('id', 'unknown')

                # Construir URL del tweet
                # Necesitamos el username, lo obtenemos de la autenticación
                # Por ahora, usar formato genérico
                post_url = f"https://twitter.com/i/web/status/{tweet_id}"

                logger.info(f"Twitter: Tweet publicado exitosamente - {tweet_id}")

                return PostResult(
                    success=True,
                    platform='twitter',
                    post_id=tweet_id,
                    post_url=post_url
                )
            else:
                # Error
                error_msg = response.text
                logger.error(f"Twitter: Error al publicar - {response.status_code}: {error_msg}")

                return PostResult(
                    success=False,
                    platform='twitter',
                    error=f"HTTP {response.status_code}: {error_msg}"
                )

        except Exception as e:
            logger.error(f"Twitter: Excepción al publicar - {e}")
            return PostResult(
                success=False,
                platform='twitter',
                error=str(e)
            )

    def get_rate_limit(self) -> Dict:
        """
        Obtener información de rate limiting

        Twitter Free Tier: 1,500 tweets/mes

        Returns:
            Diccionario con límites
        """
        return self._rate_limit_info
