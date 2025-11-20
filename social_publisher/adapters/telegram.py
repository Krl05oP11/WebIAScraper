"""
Adaptador para Telegram
"""
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

from .base import SocialMediaAdapter, PostContent, PostResult

logger = logging.getLogger(__name__)


class TelegramAdapter(SocialMediaAdapter):
    """
    Adaptador para publicar en Telegram

    Documentación: https://core.telegram.org/bots/api

    Telegram Bot API es extremadamente simple y sin límites significativos.
    Perfecto para canales personales de noticias.
    """

    API_BASE_URL = "https://api.telegram.org"
    MAX_MESSAGE_LENGTH = 4096  # Telegram permite hasta 4096 caracteres

    def __init__(self, credentials: Dict[str, str], config: Optional[Dict] = None):
        super().__init__(credentials, config)
        self.bot_token = credentials.get('bot_token')
        self.channel_id = credentials.get('channel_id')  # @canal o -100123456789

    def authenticate(self) -> bool:
        """
        Verificar autenticación con Telegram

        Telegram no requiere OAuth, solo un bot token.
        Verificamos llamando a getMe.
        """
        try:
            if not self.bot_token:
                logger.error("Telegram: bot_token no proporcionado")
                return False

            # Verificar token
            response = requests.get(
                f"{self.API_BASE_URL}/bot{self.bot_token}/getMe",
                timeout=10
            )

            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_data = bot_info.get('result', {})
                    self._authenticated = True
                    logger.info(f"Telegram: Autenticación exitosa - Bot: @{bot_data.get('username', 'unknown')}")
                    return True

            logger.error(f"Telegram: Error de autenticación - {response.status_code}")
            return False

        except Exception as e:
            logger.error(f"Telegram: Error en autenticación - {e}")
            return False

    def verify_credentials(self) -> bool:
        """Verificar credenciales"""
        return self.authenticate()

    def format_content(self, content: PostContent) -> Dict:
        """
        Formatear contenido para Telegram

        Telegram permite hasta 4096 caracteres y soporta HTML/Markdown.
        Usaremos HTML para formato más rico.

        Args:
            content: Contenido a formatear

        Returns:
            Diccionario con formato de Telegram
        """
        # Construir mensaje con formato HTML
        message_parts = []

        # Título en negrita
        if content.titulo:
            title_clean = self._escape_html(content.titulo)
            message_parts.append(f"<b>📰 {title_clean}</b>\n")

        # Descripción
        if content.descripcion:
            desc_clean = self._escape_html(content.descripcion)
            message_parts.append(f"{desc_clean}\n")

        # Categoría (si está disponible)
        if content.categoria:
            cat_clean = self._escape_html(content.categoria)
            message_parts.append(f"\n📂 <i>{cat_clean}</i>")

        # Hashtags
        if content.hashtags:
            hashtags_str = self._format_hashtags(content.hashtags)
            message_parts.append(f"\n\n{hashtags_str}")

        # URL (con preview)
        if content.url:
            url_clean = self._escape_html(content.url)
            message_parts.append(f"\n\n🔗 <a href='{url_clean}'>Leer más</a>")

        # Unir todo
        message_text = "\n".join(message_parts)

        # Truncar si excede el límite
        if len(message_text) > self.MAX_MESSAGE_LENGTH:
            message_text = message_text[:self.MAX_MESSAGE_LENGTH - 20] + "\n\n[Truncado...]"

        return {
            "chat_id": self.channel_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False  # Mostrar preview de enlaces
        }

    def publish(self, content: PostContent) -> PostResult:
        """
        Publicar contenido en Telegram

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
                        platform='telegram',
                        error='Autenticación fallida'
                    )

            if not self.channel_id:
                return PostResult(
                    success=False,
                    platform='telegram',
                    error='channel_id no configurado'
                )

            # Formatear contenido
            message_data = self.format_content(content)

            # Publicar
            response = requests.post(
                f"{self.API_BASE_URL}/bot{self.bot_token}/sendMessage",
                json=message_data,
                timeout=30
            )

            # Procesar respuesta
            if response.status_code == 200:
                response_data = response.json()

                if response_data.get('ok'):
                    # Éxito
                    result = response_data.get('result', {})
                    message_id = result.get('message_id', 'unknown')

                    # Construir URL del mensaje
                    # Formato: https://t.me/{channel_username}/{message_id}
                    # Si channel_id es numérico (chat privado), no hay URL pública
                    post_url = None
                    if isinstance(self.channel_id, str) and self.channel_id.startswith('@'):
                        channel_name = self.channel_id.lstrip('@')
                        post_url = f"https://t.me/{channel_name}/{message_id}"

                    logger.info(f"Telegram: Mensaje publicado exitosamente - {message_id}")

                    return PostResult(
                        success=True,
                        platform='telegram',
                        post_id=str(message_id),
                        post_url=post_url
                    )
                else:
                    error_msg = response_data.get('description', 'Unknown error')
                    logger.error(f"Telegram: Error al publicar - {error_msg}")
                    return PostResult(
                        success=False,
                        platform='telegram',
                        error=error_msg
                    )
            else:
                # Error HTTP
                error_msg = response.text
                logger.error(f"Telegram: Error al publicar - {response.status_code}: {error_msg}")

                return PostResult(
                    success=False,
                    platform='telegram',
                    error=f"HTTP {response.status_code}: {error_msg}"
                )

        except Exception as e:
            logger.error(f"Telegram: Excepción al publicar - {e}")
            return PostResult(
                success=False,
                platform='telegram',
                error=str(e)
            )

    def get_rate_limit(self) -> Dict:
        """
        Obtener información de rate limiting

        Telegram tiene flood control pero es muy generoso para bots.
        Límite: ~30 mensajes/segundo al mismo chat

        Returns:
            Diccionario con límites
        """
        return {
            'limit': 10000,  # Muy alto, prácticamente ilimitado para uso normal
            'remaining': 10000,
            'reset_at': datetime.utcnow() + timedelta(days=1)
        }

    def _escape_html(self, text: str) -> str:
        """
        Escapar caracteres especiales de HTML para Telegram

        Args:
            text: Texto a escapar

        Returns:
            Texto escapado
        """
        if not text:
            return ""

        replacements = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
        }

        for char, escape in replacements.items():
            text = text.replace(char, escape)

        return text
