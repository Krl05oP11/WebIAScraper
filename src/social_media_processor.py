"""
Procesador de contenido para redes sociales
Integra traducción y optimización para diferentes plataformas
"""
import logging
from datetime import datetime
from typing import List, Dict, Optional
from src.translation_service import TranslationService
from src.models import APublicar, db

logger = logging.getLogger(__name__)


class SocialMediaProcessor:
    """
    Procesador que traduce y optimiza contenido para redes sociales
    """

    def __init__(self, anthropic_api_key: Optional[str] = None):
        """
        Inicializa el procesador

        Args:
            anthropic_api_key: API key de Anthropic (opcional, usa .env si no se provee)
        """
        try:
            self.translation_service = TranslationService(api_key=anthropic_api_key)
            logger.info("✓ Servicio de traducción inicializado")
        except Exception as e:
            logger.error(f"✗ Error inicializando servicio de traducción: {e}")
            raise

    def process_item(self, item_id: int) -> bool:
        """
        Procesa un único item de APublicar

        Args:
            item_id: ID del item en la tabla APublicar

        Returns:
            True si se procesó exitosamente, False en caso contrario
        """
        try:
            # Obtener item de la base de datos
            item = APublicar.query.get(item_id)

            if not item:
                logger.error(f"Item {item_id} no encontrado")
                return False

            if item.procesado:
                logger.warning(f"Item {item_id} ya fue procesado anteriormente")
                return True

            logger.info(f"Procesando item {item_id}: {item.titulo[:50]}...")

            # Traducir y optimizar
            result = self.translation_service.translate_and_optimize(
                titulo=item.titulo,
                texto=item.texto,
                url=item.url
            )

            # Actualizar item con resultados
            item.titulo_es = result['titulo_es']
            item.texto_es = result['texto_es']
            item.resumen_corto = result['resumen_corto']
            item.resumen_medio = result['resumen_medio']
            item.resumen_largo = result['resumen_largo']
            item.hashtags = result['hashtags']
            item.categoria = result['categoria']
            item.procesado = True
            item.processed_at = datetime.utcnow()

            # Guardar en base de datos
            db.session.commit()

            logger.info(f"✓ Item {item_id} procesado exitosamente")
            logger.info(f"  - Categoría: {item.categoria}")
            logger.info(f"  - Hashtags: {item.hashtags}")

            return True

        except Exception as e:
            logger.error(f"✗ Error procesando item {item_id}: {e}")
            db.session.rollback()
            return False

    def process_batch(self, item_ids: List[int]) -> Dict[str, int]:
        """
        Procesa un lote de items

        Args:
            item_ids: Lista de IDs de items a procesar

        Returns:
            Diccionario con estadísticas de procesamiento
        """
        stats = {
            'total': len(item_ids),
            'exitosos': 0,
            'fallidos': 0,
            'ya_procesados': 0
        }

        logger.info(f"Iniciando procesamiento de {len(item_ids)} items...")

        for item_id in item_ids:
            # Verificar si ya fue procesado
            item = APublicar.query.get(item_id)
            if item and item.procesado:
                stats['ya_procesados'] += 1
                continue

            # Procesar item
            if self.process_item(item_id):
                stats['exitosos'] += 1
            else:
                stats['fallidos'] += 1

        logger.info(f"Procesamiento completado: {stats['exitosos']} exitosos, "
                   f"{stats['fallidos']} fallidos, {stats['ya_procesados']} ya procesados")

        return stats

    def process_all_pending(self, limit: Optional[int] = None) -> Dict[str, int]:
        """
        Procesa todos los items pendientes (no procesados)

        Args:
            limit: Número máximo de items a procesar (None = todos)

        Returns:
            Diccionario con estadísticas de procesamiento
        """
        # Obtener items pendientes - SOLO fase 'pendiente' o 'scrapeado'
        # NO procesar items que ya tienen fase='procesado' aunque procesado=False
        query = APublicar.query.filter(
            APublicar.fase.in_(['pendiente', 'scrapeado'])
        )

        if limit:
            query = query.limit(limit)

        pending_items = query.all()
        item_ids = [item.id for item in pending_items]

        logger.info(f"Encontrados {len(item_ids)} items pendientes de procesar")

        if not item_ids:
            return {'total': 0, 'exitosos': 0, 'fallidos': 0, 'ya_procesados': 0}

        return self.process_batch(item_ids)

    def reprocess_item(self, item_id: int, force: bool = False) -> bool:
        """
        Re-procesa un item ya procesado

        Args:
            item_id: ID del item
            force: Si es True, fuerza el reprocesamiento aunque ya esté procesado

        Returns:
            True si se reprocesó exitosamente
        """
        try:
            item = APublicar.query.get(item_id)

            if not item:
                logger.error(f"Item {item_id} no encontrado")
                return False

            if not force and not item.procesado:
                logger.info(f"Item {item_id} no ha sido procesado aún. Procesando por primera vez...")
                return self.process_item(item_id)

            logger.info(f"Re-procesando item {item_id}...")

            # Marcar como no procesado temporalmente
            item.procesado = False
            db.session.commit()

            # Procesar nuevamente
            return self.process_item(item_id)

        except Exception as e:
            logger.error(f"Error re-procesando item {item_id}: {e}")
            db.session.rollback()
            return False

    def get_processing_stats(self) -> Dict[str, int]:
        """
        Obtiene estadísticas de procesamiento

        Returns:
            Diccionario con estadísticas
        """
        total = APublicar.query.count()
        procesados = APublicar.query.filter_by(procesado=True).count()
        pendientes = total - procesados

        return {
            'total': total,
            'procesados': procesados,
            'pendientes': pendientes,
            'porcentaje_procesado': round((procesados / total * 100) if total > 0 else 0, 2)
        }

    def get_processed_by_category(self) -> Dict[str, int]:
        """
        Obtiene conteo de items procesados por categoría

        Returns:
            Diccionario con categorías y conteos
        """
        items = APublicar.query.filter_by(procesado=True).all()

        categories = {}
        for item in items:
            cat = item.categoria or 'Sin categoría'
            categories[cat] = categories.get(cat, 0) + 1

        return categories

    def export_for_social_media(
        self,
        item_ids: Optional[List[int]] = None,
        platform: Optional[str] = None
    ) -> List[Dict]:
        """
        Exporta items procesados en formato para redes sociales

        Args:
            item_ids: IDs específicos a exportar (None = todos los procesados)
            platform: Plataforma específica ('twitter', 'facebook', 'instagram', None = todas)

        Returns:
            Lista de items en formato JSON para RRSS
        """
        # Obtener items
        if item_ids:
            items = APublicar.query.filter(
                APublicar.id.in_(item_ids),
                APublicar.procesado == True
            ).all()
        else:
            items = APublicar.query.filter_by(procesado=True).all()

        # Convertir a formato RRSS
        export_data = []

        for item in items:
            data = item.to_social_media_json()

            # Si se especifica plataforma, filtrar contenido
            if platform:
                platform_map = {
                    'twitter': 'twitter_linkedin',
                    'linkedin': 'twitter_linkedin',
                    'facebook': 'facebook',
                    'instagram': 'instagram_whatsapp',
                    'whatsapp': 'instagram_whatsapp'
                }

                if platform.lower() in platform_map:
                    content_key = platform_map[platform.lower()]
                    data['contenido'] = {platform.lower(): data['contenido'][content_key]}

            export_data.append(data)

        logger.info(f"Exportados {len(export_data)} items para {platform or 'todas las plataformas'}")

        return export_data


def test_processor():
    """
    Función de prueba del procesador
    """
    from flask import Flask
    from models import init_db
    import os

    # Crear app Flask para contexto de DB
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    init_db(app)

    with app.app_context():
        # Crear procesador
        processor = SocialMediaProcessor()

        # Obtener estadísticas
        stats = processor.get_processing_stats()
        print(f"\n{'='*80}")
        print("ESTADÍSTICAS DE PROCESAMIENTO")
        print(f"{'='*80}")
        print(f"Total de items: {stats['total']}")
        print(f"Procesados: {stats['procesados']}")
        print(f"Pendientes: {stats['pendientes']}")
        print(f"Porcentaje procesado: {stats['porcentaje_procesado']}%")
        print()

        # Procesar pendientes (máximo 3 para prueba)
        if stats['pendientes'] > 0:
            print("Procesando items pendientes...")
            result = processor.process_all_pending(limit=3)
            print(f"Resultado: {result}")

        # Mostrar distribución por categorías
        categories = processor.get_processed_by_category()
        if categories:
            print(f"\n{'='*80}")
            print("DISTRIBUCIÓN POR CATEGORÍAS")
            print(f"{'='*80}")
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                print(f"  {cat}: {count}")


if __name__ == '__main__':
    # Configurar logging para pruebas
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Cargar variables de entorno
    from dotenv import load_dotenv
    load_dotenv()

    test_processor()
