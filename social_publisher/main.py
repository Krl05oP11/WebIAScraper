"""
SocialPublisher - Punto de entrada principal
"""
import logging
import sys
import time
import signal
from datetime import datetime

from .publisher_service import PublisherService
from .config.settings import SocialPublisherConfig

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/social_publisher.log')
    ]
)
logger = logging.getLogger(__name__)


class SocialPublisher:
    """
    Aplicación principal de SocialPublisher

    Se ejecuta en modo daemon, consultando periódicamente
    la API de WebIAScraper para obtener noticias pendientes
    y publicarlas en las redes sociales configuradas.
    """

    def __init__(self):
        self.config = SocialPublisherConfig()
        self.service = PublisherService(config=self.config)
        self.running = True

        # Registrar señales para shutdown graceful
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Manejar señales de shutdown"""
        logger.info(f"📡 Señal {signum} recibida, iniciando shutdown...")
        self.running = False

    def start(self):
        """Iniciar el servicio"""
        logger.info("=" * 80)
        logger.info("🚀 SocialPublisher v0.1.0 - Iniciando...")
        logger.info("=" * 80)

        # Mostrar configuración
        logger.info(f"📍 WebIAScraper API: {self.config.WEBIASCRAPER_API_URL}")
        logger.info(f"⏱️  Intervalo de polling: {self.config.POLL_INTERVAL_SECONDS} segundos")
        logger.info(f"📊 Máximo de noticias por ciclo: {self.config.MAX_NEWS_PER_CYCLE}")

        # Mostrar plataformas disponibles
        stats = self.service.get_stats()
        if stats['adapters_available'] > 0:
            logger.info(f"✅ Plataformas configuradas: {', '.join(stats['platforms'])}")
        else:
            logger.error("❌ No hay plataformas configuradas. Verifica las credenciales.")
            return

        # Iniciar worker
        self.service.start_worker()

        # Loop principal
        logger.info("🔄 Iniciando loop de polling...")
        cycle_count = 0

        while self.running:
            try:
                cycle_count += 1
                logger.info(f"\n{'=' * 60}")
                logger.info(f"📅 Ciclo #{cycle_count} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"{'=' * 60}")

                # Ejecutar ciclo
                self.service.run_cycle()

                # Mostrar stats
                stats = self.service.get_stats()
                logger.info(f"📊 Queue: {stats['queue_size']} items pendientes")

                # Esperar hasta el próximo ciclo
                logger.info(f"💤 Esperando {self.config.POLL_INTERVAL_SECONDS} segundos hasta el próximo ciclo...")
                time.sleep(self.config.POLL_INTERVAL_SECONDS)

            except Exception as e:
                logger.error(f"❌ Error en loop principal: {e}", exc_info=True)
                time.sleep(60)  # Esperar 1 minuto antes de reintentar

        # Shutdown
        self.shutdown()

    def shutdown(self):
        """Shutdown graceful del servicio"""
        logger.info("\n" + "=" * 80)
        logger.info("🛑 Iniciando shutdown graceful...")
        logger.info("=" * 80)

        # Detener worker
        self.service.stop_worker()

        # Esperar a que la queue se vacíe (máximo 30 segundos)
        logger.info("⏳ Esperando a que se procesen los items pendientes...")
        self.service.publication_queue.join()

        logger.info("✅ Shutdown completado")
        logger.info("=" * 80)


def main():
    """Función principal"""
    try:
        app = SocialPublisher()
        app.start()
    except KeyboardInterrupt:
        logger.info("\n⚠️ Interrupción manual detectada")
    except Exception as e:
        logger.error(f"❌ Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
