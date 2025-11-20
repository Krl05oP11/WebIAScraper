"""
Clase base y tipos para adaptadores de redes sociales
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Optional, List
from datetime import datetime


@dataclass
class PostContent:
    """
    Contenido a publicar en redes sociales
    """
    titulo: str
    descripcion: str
    url: Optional[str] = None
    image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    categoria: Optional[str] = None

    def __post_init__(self):
        """Inicializar listas vacías si no se proporcionan"""
        if self.tags is None:
            self.tags = []
        if self.hashtags is None:
            self.hashtags = []


@dataclass
class PostResult:
    """
    Resultado de publicación en una plataforma
    """
    success: bool
    platform: str
    post_id: Optional[str] = None
    error: Optional[str] = None
    post_url: Optional[str] = None
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        """Inicializar timestamp si no se proporciona"""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class SocialMediaAdapter(ABC):
    """
    Clase base abstracta para adaptadores de redes sociales

    Cada plataforma (LinkedIn, Twitter, etc.) debe implementar
    esta interfaz para estandarizar la publicación.
    """

    def __init__(self, credentials: Dict[str, str], config: Optional[Dict] = None):
        """
        Inicializar adaptador

        Args:
            credentials: Diccionario con credenciales de la plataforma
            config: Configuración adicional opcional
        """
        self.credentials = credentials
        self.config = config or {}
        self.platform_name = self.__class__.__name__.replace('Adapter', '').lower()
        self._authenticated = False

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Autenticar con la plataforma

        Returns:
            True si la autenticación fue exitosa
        """
        pass

    @abstractmethod
    def format_content(self, content: PostContent) -> Dict:
        """
        Formatear contenido para la plataforma específica

        Cada plataforma tiene sus propios límites y formatos.
        Este método debe adaptar el contenido a esos requisitos.

        Args:
            content: Contenido a formatear

        Returns:
            Diccionario con contenido formateado para la API de la plataforma
        """
        pass

    @abstractmethod
    def publish(self, content: PostContent) -> PostResult:
        """
        Publicar contenido en la plataforma

        Args:
            content: Contenido a publicar

        Returns:
            Resultado de la publicación
        """
        pass

    @abstractmethod
    def get_rate_limit(self) -> Dict:
        """
        Obtener información de límites de rate limiting

        Returns:
            Diccionario con información de límites:
            {
                'limit': int,  # límite total
                'remaining': int,  # llamadas restantes
                'reset_at': datetime  # cuándo se resetea
            }
        """
        pass

    @abstractmethod
    def verify_credentials(self) -> bool:
        """
        Verificar que las credenciales son válidas

        Returns:
            True si las credenciales son válidas
        """
        pass

    def is_authenticated(self) -> bool:
        """
        Verificar si el adaptador está autenticado

        Returns:
            True si está autenticado
        """
        return self._authenticated

    def _truncate_text(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncar texto a una longitud máxima

        Args:
            text: Texto a truncar
            max_length: Longitud máxima
            suffix: Sufijo a añadir si se trunca

        Returns:
            Texto truncado
        """
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)].rstrip() + suffix

    def _format_hashtags(self, hashtags: List[str], prefix: str = "#") -> str:
        """
        Formatear lista de hashtags a string

        Args:
            hashtags: Lista de hashtags
            prefix: Prefijo a añadir (por defecto #)

        Returns:
            String con hashtags formateados
        """
        if not hashtags:
            return ""

        # Limpiar hashtags (remover # si ya existe)
        clean_tags = [tag.lstrip('#') for tag in hashtags]

        # Añadir prefix
        formatted = [f"{prefix}{tag}" for tag in clean_tags]

        return " ".join(formatted)

    def __repr__(self):
        return f"<{self.__class__.__name__} platform={self.platform_name} authenticated={self._authenticated}>"
