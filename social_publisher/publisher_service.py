"""
Servicio principal de publicación en redes sociales
"""
import logging
import requests
import time
from typing import List, Dict, Optional
from datetime import datetime
from queue import Queue, Empty
from threading import Thread, Event

from .adapters import (
    PostContent,
    PostResult,
    LinkedInAdapter,
    TwitterAdapter,
    BlueskyAdapter,
    TelegramAdapter
)
from .config.settings import SocialPublisherConfig

logger = logging.getLogger(__name__)


class PublisherService:
    """
    Servicio que coordina la publicación de noticias en múltiples plataformas

    Features:
    - Queue interno para manejar publicaciones
    - Retry logic con backoff exponencial
    - Rate limiting por plataforma
    - Comunicación con WebIAScraper API
    """

    def __init__(self, config: Optional[SocialPublisherConfig] = None):
        """
        Inicializar servicio

        Args:
            config: Configuración (usa SocialPublisherConfig por defecto)
        """
        self.config = config or SocialPublisherConfig()
        self.adapters = {}
        self.publication_queue = Queue()
        self.stop_event = Event()
        self.worker_thread = None

        # Inicializar adaptadores
        self._init_adapters()

    def _init_adapters(self):
        """Inicializar adaptadores para plataformas habilitadas"""
        adapter_classes = {
            'linkedin': LinkedInAdapter,
            'twitter': TwitterAdapter,
            'bluesky': BlueskyAdapter,
            'telegram': TelegramAdapter
        }

        enabled_platforms = self.config.get_enabled_and_configured_platforms()

        for platform in enabled_platforms:
            if platform not in adapter_classes:
                logger.warning(f"Plataforma desconocida: {platform}")
                continue

            try:
                # Obtener credenciales
                credentials = self.config.get_platform_credentials(platform)

                # Crear adaptador
                adapter_class = adapter_classes[platform]
                adapter = adapter_class(credentials=credentials)

                # Autenticar
                if adapter.authenticate():
                    self.adapters[platform] = adapter
                    logger.info(f"✅ {platform.capitalize()}: Adaptador inicializado")
                else:
                    logger.error(f"❌ {platform.capitalize()}: Error de autenticación")

            except Exception as e:
                logger.error(f"❌ {platform.capitalize()}: Error al inicializar - {e}")

        if not self.adapters:
            logger.warning("⚠️ No hay adaptadores disponibles. Verifica las credenciales.")

    def fetch_news_to_publish(self, limit: int = 10) -> List[Dict]:
        """
        Obtener noticias pendientes de publicar desde WebIAScraper API

        Args:
            limit: Máximo de noticias a obtener

        Returns:
            Lista de noticias
        """
        try:
            url = f"{self.config.WEBIASCRAPER_API_URL}/api/news/to-publish"
            params = {
                'procesados': 'true',
                'limit': limit
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                noticias = data.get('noticias', [])
                logger.info(f"📥 Obtenidas {len(noticias)} noticias para publicar")
                return noticias
            else:
                logger.error(f"Error al obtener noticias: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error al conectar con WebIAScraper: {e}")
            return []

    def mark_as_published(self, noticia_id: int, platform: str,
                         post_id: Optional[str] = None,
                         post_url: Optional[str] = None,
                         error: Optional[str] = None) -> bool:
        """
        Marcar noticia como publicada en WebIAScraper

        Args:
            noticia_id: ID de la noticia
            platform: Plataforma
            post_id: ID del post (si fue exitoso)
            post_url: URL del post (si fue exitoso)
            error: Mensaje de error (si falló)

        Returns:
            True si se marcó exitosamente
        """
        try:
            url = f"{self.config.WEBIASCRAPER_API_URL}/api/news/{noticia_id}/mark-published"

            payload = {
                'platform': platform,
                'post_id': post_id,
                'post_url': post_url,
                'error': error
            }

            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                logger.info(f"✅ Noticia {noticia_id} marcada como publicada en {platform}")
                return True
            else:
                logger.error(f"Error al marcar noticia: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error al marcar noticia como publicada: {e}")
            return False

    def publish_to_platform(self, noticia: Dict, platform: str) -> PostResult:
        """
        Publicar una noticia en una plataforma específica

        Args:
            noticia: Datos de la noticia
            platform: Nombre de la plataforma

        Returns:
            Resultado de la publicación
        """
        if platform not in self.adapters:
            return PostResult(
                success=False,
                platform=platform,
                error=f"Adaptador no disponible"
            )

        try:
            adapter = self.adapters[platform]

            # Crear PostContent
            content = PostContent(
                titulo=noticia.get('titulo_es') or noticia.get('titulo', ''),
                descripcion=noticia.get('resumen_corto', '') or noticia.get('texto_es', ''),
                url=noticia.get('url'),
                hashtags=noticia.get('hashtags', '').split(',') if noticia.get('hashtags') else [],
                tags=noticia.get('temas', '').split(',') if noticia.get('temas') else [],
                categoria=noticia.get('categoria')
            )

            # Publicar
            result = adapter.publish(content)

            # Marcar en WebIAScraper
            self.mark_as_published(
                noticia_id=noticia['id'],
                platform=platform,
                post_id=result.post_id if result.success else None,
                post_url=result.post_url if result.success else None,
                error=result.error if not result.success else None
            )

            return result

        except Exception as e:
            logger.error(f"Error al publicar en {platform}: {e}")
            return PostResult(
                success=False,
                platform=platform,
                error=str(e)
            )

    def publish_news(self, noticia: Dict, platforms: Optional[List[str]] = None) -> Dict[str, PostResult]:
        """
        Publicar una noticia en múltiples plataformas

        Args:
            noticia: Datos de la noticia
            platforms: Lista de plataformas (None = todas las disponibles)

        Returns:
            Diccionario con resultados por plataforma
        """
        if platforms is None:
            platforms = list(self.adapters.keys())

        results = {}

        for platform in platforms:
            if platform not in self.adapters:
                logger.warning(f"Saltando plataforma no disponible: {platform}")
                continue

            logger.info(f"📤 Publicando noticia {noticia['id']} en {platform}...")

            result = self.publish_to_platform(noticia, platform)
            results[platform] = result

            if result.success:
                logger.info(f"✅ {platform}: Publicación exitosa")
            else:
                logger.error(f"❌ {platform}: {result.error}")

            # Delay entre plataformas para evitar flood
            time.sleep(2)

        return results

    def process_queue(self):
        """
        Worker thread que procesa la queue de publicaciones
        """
        logger.info("🚀 Worker de publicación iniciado")

        while not self.stop_event.is_set():
            try:
                # Obtener item de la queue (timeout 5 segundos)
                item = self.publication_queue.get(timeout=5)

                noticia = item['noticia']
                platforms = item.get('platforms')

                logger.info(f"📋 Procesando noticia {noticia['id']} de la queue")

                # Publicar
                results = self.publish_news(noticia, platforms)

                # Marcar como procesado
                self.publication_queue.task_done()

            except Empty:
                # No hay items en la queue, continuar esperando
                continue
            except Exception as e:
                logger.error(f"Error procesando queue: {e}")

        logger.info("🛑 Worker de publicación detenido")

    def start_worker(self):
        """Iniciar worker thread para procesar queue"""
        if self.worker_thread and self.worker_thread.is_alive():
            logger.warning("Worker ya está en ejecución")
            return

        self.stop_event.clear()
        self.worker_thread = Thread(target=self.process_queue, daemon=True)
        self.worker_thread.start()
        logger.info("✅ Worker thread iniciado")

    def stop_worker(self):
        """Detener worker thread"""
        logger.info("🛑 Deteniendo worker...")
        self.stop_event.set()

        if self.worker_thread:
            self.worker_thread.join(timeout=10)
            logger.info("✅ Worker detenido")

    def enqueue_news(self, noticia: Dict, platforms: Optional[List[str]] = None):
        """
        Añadir noticia a la queue de publicación

        Args:
            noticia: Datos de la noticia
            platforms: Lista de plataformas (None = todas)
        """
        self.publication_queue.put({
            'noticia': noticia,
            'platforms': platforms
        })
        logger.info(f"📥 Noticia {noticia['id']} añadida a la queue")

    def run_cycle(self):
        """
        Ejecutar un ciclo de polling y publicación

        Este método se puede llamar periódicamente para:
        1. Obtener noticias pendientes
        2. Añadirlas a la queue
        """
        logger.info("🔄 Iniciando ciclo de publicación...")

        # Obtener noticias pendientes
        noticias = self.fetch_news_to_publish(limit=self.config.MAX_NEWS_PER_CYCLE)

        if not noticias:
            logger.info("ℹ️ No hay noticias pendientes")
            return

        # Añadir a queue
        for noticia in noticias:
            self.enqueue_news(noticia)

        logger.info(f"✅ Ciclo completado - {len(noticias)} noticias en queue")

    def get_stats(self) -> Dict:
        """
        Obtener estadísticas del servicio

        Returns:
            Diccionario con estadísticas
        """
        return {
            'adapters_available': len(self.adapters),
            'platforms': list(self.adapters.keys()),
            'queue_size': self.publication_queue.qsize(),
            'worker_running': self.worker_thread.is_alive() if self.worker_thread else False
        }
