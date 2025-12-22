"""
Configuración del proyecto WebIAScrap
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class Config:
    """Configuración base"""

    # Aplicación
    APP_NAME = os.getenv('APP_NAME', 'WebIAScrap')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    WTF_CSRF_SECRET_KEY = os.getenv('WTF_CSRF_SECRET_KEY', 'dev-csrf-key')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Server
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))

    # Database
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://webiauser:changeme123@localhost:5432/webiascrap'
    )
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = DEBUG

    # NewsAPI
    NEWSAPI_KEY = os.getenv('NEWSAPI_KEY', '')

    # Anthropic API (para traducción con Claude)
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')

    # Scraping Configuration
    NEWS_SOURCES = os.getenv('NEWS_SOURCES', 'techcrunch,wired,the-verge').split(',')
    MAX_NEWS_COUNT = int(os.getenv('MAX_NEWS_COUNT', 100))  # Aumentado de 30 a 100 para más variedad
    SCRAPE_INTERVAL_HOURS = int(os.getenv('SCRAPE_INTERVAL_HOURS', 24))

    # News Keywords
    NEWS_KEYWORDS = os.getenv(
        'NEWS_KEYWORDS',
        'artificial intelligence,AI,machine learning,data science,neural networks,deep learning'
    ).split(',')

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', '/app/logs/webiascrap.log')


class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


class TestingConfig(Config):
    """Configuración de testing"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Retorna la configuración basada en el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
