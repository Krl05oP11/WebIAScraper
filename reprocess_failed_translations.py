"""
Script para re-procesar noticias con traducciones fallidas
Identifica items donde titulo_es == titulo (no fueron traducidos) y los reprocesa
"""
import logging
from flask import Flask
from src.models import APublicar, init_db
from src.social_media_processor import SocialMediaProcessor
from dotenv import load_dotenv
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def find_failed_translations():
    """
    Encuentra noticias donde titulo_es == titulo (traducciones fallidas)
    """
    # Buscar items procesados donde la traducción falló
    failed_items = APublicar.query.filter(
        APublicar.procesado == True,
        APublicar.titulo_es == APublicar.titulo
    ).all()

    logger.info(f"Encontradas {len(failed_items)} noticias con traducciones fallidas")

    return [item.id for item in failed_items]

def reprocess_all_failed():
    """
    Re-procesa todas las noticias con traducciones fallidas
    """
    # Encontrar noticias fallidas
    failed_ids = find_failed_translations()

    if not failed_ids:
        logger.info("✓ No hay noticias con traducciones fallidas")
        return

    logger.info(f"\n{'='*80}")
    logger.info(f"RE-PROCESANDO {len(failed_ids)} NOTICIAS")
    logger.info(f"{'='*80}\n")

    # Crear procesador
    processor = SocialMediaProcessor()

    # Re-procesar cada noticia
    stats = {
        'exitosas': 0,
        'fallidas': 0
    }

    for i, item_id in enumerate(failed_ids, 1):
        logger.info(f"\n[{i}/{len(failed_ids)}] Re-procesando noticia ID {item_id}...")

        try:
            if processor.reprocess_item(item_id, force=True):
                stats['exitosas'] += 1
                logger.info(f"  ✓ Noticia {item_id} re-procesada exitosamente")
            else:
                stats['fallidas'] += 1
                logger.error(f"  ✗ Fallo al re-procesar noticia {item_id}")
        except Exception as e:
            stats['fallidas'] += 1
            logger.error(f"  ✗ Error re-procesando noticia {item_id}: {e}")

    # Resumen final
    logger.info(f"\n{'='*80}")
    logger.info("RESUMEN FINAL")
    logger.info(f"{'='*80}")
    logger.info(f"Total procesadas: {len(failed_ids)}")
    logger.info(f"Exitosas: {stats['exitosas']}")
    logger.info(f"Fallidas: {stats['fallidas']}")
    logger.info(f"Tasa de éxito: {(stats['exitosas']/len(failed_ids)*100):.1f}%")

def main():
    """
    Función principal
    """
    # Cargar variables de entorno
    load_dotenv()

    # Verificar API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        logger.error("✗ ANTHROPIC_API_KEY no configurada en .env")
        return

    # Crear app Flask para contexto de DB
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)

    with app.app_context():
        # Mostrar estadísticas iniciales
        total = APublicar.query.filter_by(procesado=True).count()
        failed = APublicar.query.filter(
            APublicar.procesado == True,
            APublicar.titulo_es == APublicar.titulo
        ).count()

        logger.info(f"\n{'='*80}")
        logger.info("ESTADÍSTICAS INICIALES")
        logger.info(f"{'='*80}")
        logger.info(f"Noticias procesadas: {total}")
        logger.info(f"Con traducciones fallidas: {failed}")
        logger.info(f"Porcentaje fallidas: {(failed/total*100):.1f}%")

        # Confirmar antes de proceder
        if failed > 0:
            print(f"\n¿Deseas re-procesar las {failed} noticias con traducciones fallidas? (s/n): ", end='')
            respuesta = input().strip().lower()

            if respuesta == 's':
                reprocess_all_failed()
            else:
                logger.info("Cancelado por el usuario")
        else:
            logger.info("\n✓ No hay noticias que re-procesar")

if __name__ == '__main__':
    main()
