"""
Configuración del SocialPublisher
"""
import os
from typing import Dict, List


class SocialPublisherConfig:
    """
    Configuración para el microservicio SocialPublisher
    """

    # WebIAScraper API
    WEBIASCRAPER_API_URL = os.getenv('WEBIASCRAPER_API_URL', 'http://app:8000')
    WEBIASCRAPER_API_KEY = os.getenv('WEBIASCRAPER_API_KEY', '')

    # Plataformas habilitadas
    ENABLED_PLATFORMS = os.getenv(
        'ENABLED_PLATFORMS',
        'linkedin,twitter,bluesky,telegram'
    ).split(',')

    # Intervalo de polling (segundos)
    POLL_INTERVAL_SECONDS = int(os.getenv('POLL_INTERVAL_SECONDS', '300'))  # 5 minutos

    # Número máximo de noticias a procesar por ciclo
    MAX_NEWS_PER_CYCLE = int(os.getenv('MAX_NEWS_PER_CYCLE', '5'))

    # Retry configuration
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    RETRY_DELAY_SECONDS = int(os.getenv('RETRY_DELAY_SECONDS', '60'))
    RETRY_BACKOFF_MULTIPLIER = float(os.getenv('RETRY_BACKOFF_MULTIPLIER', '2.0'))

    # LinkedIn credentials
    LINKEDIN_CLIENT_ID = os.getenv('LINKEDIN_CLIENT_ID', '')
    LINKEDIN_CLIENT_SECRET = os.getenv('LINKEDIN_CLIENT_SECRET', '')
    LINKEDIN_ACCESS_TOKEN = os.getenv('LINKEDIN_ACCESS_TOKEN', '')
    LINKEDIN_PERSON_URN = os.getenv('LINKEDIN_PERSON_URN', '')  # urn:li:person:xxxxx

    # Twitter/X credentials
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY', '')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET', '')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN', '')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET', '')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')

    # Bluesky credentials
    BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE', '')  # usuario.bsky.social
    BLUESKY_APP_PASSWORD = os.getenv('BLUESKY_APP_PASSWORD', '')

    # Telegram credentials
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')  # @nombre_canal o -100123456789

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/app/logs/social_publisher.log')

    @classmethod
    def get_platform_credentials(cls, platform: str) -> Dict[str, str]:
        """
        Obtener credenciales para una plataforma específica

        Args:
            platform: Nombre de la plataforma (linkedin, twitter, bluesky, telegram)

        Returns:
            Diccionario con credenciales
        """
        credentials_map = {
            'linkedin': {
                'client_id': cls.LINKEDIN_CLIENT_ID,
                'client_secret': cls.LINKEDIN_CLIENT_SECRET,
                'access_token': cls.LINKEDIN_ACCESS_TOKEN,
                'person_urn': cls.LINKEDIN_PERSON_URN,
            },
            'twitter': {
                'api_key': cls.TWITTER_API_KEY,
                'api_secret': cls.TWITTER_API_SECRET,
                'access_token': cls.TWITTER_ACCESS_TOKEN,
                'access_token_secret': cls.TWITTER_ACCESS_TOKEN_SECRET,
                'bearer_token': cls.TWITTER_BEARER_TOKEN,
            },
            'bluesky': {
                'handle': cls.BLUESKY_HANDLE,
                'app_password': cls.BLUESKY_APP_PASSWORD,
            },
            'telegram': {
                'bot_token': cls.TELEGRAM_BOT_TOKEN,
                'channel_id': cls.TELEGRAM_CHANNEL_ID,
            }
        }

        return credentials_map.get(platform, {})

    @classmethod
    def is_platform_configured(cls, platform: str) -> bool:
        """
        Verificar si una plataforma está configurada con credenciales

        Args:
            platform: Nombre de la plataforma

        Returns:
            True si tiene credenciales configuradas
        """
        credentials = cls.get_platform_credentials(platform)

        if not credentials:
            return False

        # Verificar que al menos una credencial esté presente
        return any(value for value in credentials.values())

    @classmethod
    def get_enabled_and_configured_platforms(cls) -> List[str]:
        """
        Obtener lista de plataformas habilitadas Y configuradas

        Returns:
            Lista de plataformas listas para usar
        """
        return [
            platform.strip()
            for platform in cls.ENABLED_PLATFORMS
            if cls.is_platform_configured(platform.strip())
        ]
