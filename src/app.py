"""
WebIAScrap - Aplicación Flask Principal
"""
import logging
import sys
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_wtf.csrf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text

# Agregar el directorio raíz al path
sys.path.insert(0, '/app')

from config.settings import get_config
from src.models import db, init_db, Noticia, APublicar
from src.news_scraper import NewsScraper
from src.technical_sources_scraper import TechnicalSourcesScraper
from src.social_media_processor import SocialMediaProcessor

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Crear aplicación Flask
app = Flask(__name__)

# Cargar configuración
config = get_config()
app.config.from_object(config)

# Inicializar extensiones
csrf = CSRFProtect(app)
init_db(app)

# Scheduler para scraping automático
scheduler = BackgroundScheduler()


def scrape_and_save_news():
    """
    Función que ejecuta el scraping y guarda las noticias en la BD
    Combina NewsAPI y fuentes técnicas especializadas
    """
    with app.app_context():
        try:
            logger.info("🔍 Iniciando scraping de noticias...")
            all_noticias = []

            # 1. Scraping desde NewsAPI (fuentes generales)
            api_key = app.config.get('NEWSAPI_KEY')
            if api_key and api_key != 'your-newsapi-key-here':
                logger.info("📰 Scraping desde NewsAPI...")
                scraper = NewsScraper(
                    api_key=api_key,
                    keywords=app.config.get('NEWS_KEYWORDS', []),
                    sources=app.config.get('NEWS_SOURCES', None)
                )
                noticias_newsapi = scraper.fetch_news(max_results=15)
                all_noticias.extend(noticias_newsapi)
                logger.info(f"✓ NewsAPI: {len(noticias_newsapi)} noticias obtenidas")
            else:
                logger.warning("⚠️ NewsAPI key no configurada. Saltando NewsAPI.")

            # 2. Scraping desde fuentes técnicas (RSS)
            logger.info("🔬 Scraping desde fuentes técnicas...")
            technical_scraper = TechnicalSourcesScraper(
                sources=['huggingface', 'arxiv_ai', 'google_ai', 'openai', 'deepmind'],
                days_back=7
            )
            noticias_tecnicas = technical_scraper.fetch_all_sources(max_per_source=5)
            all_noticias.extend(noticias_tecnicas)
            logger.info(f"✓ Fuentes técnicas: {len(noticias_tecnicas)} artículos obtenidos")

            if not all_noticias:
                logger.warning("⚠️ No se encontraron noticias en ninguna fuente")
                return

            # Guardar en base de datos
            nuevas = 0
            duplicadas = 0

            for noticia_data in all_noticias:
                try:
                    # Verificar si ya existe por URL
                    existe = Noticia.query.filter_by(url=noticia_data['url']).first()
                    if existe:
                        duplicadas += 1
                        continue

                    # Crear nueva noticia
                    noticia = Noticia(
                        titulo=noticia_data['titulo'],
                        texto=noticia_data['texto'],
                        url=noticia_data['url'],
                        fecha_hora=noticia_data['fecha_hora'],
                        temas=noticia_data['temas']
                    )

                    db.session.add(noticia)
                    nuevas += 1

                except Exception as e:
                    logger.error(f"Error guardando noticia: {e}")
                    continue

            # Commit de todas las noticias
            db.session.commit()

            # Mantener solo las últimas 30 noticias
            total_noticias = Noticia.query.count()
            if total_noticias > app.config.get('MAX_NEWS_COUNT', 30):
                # Obtener las más antiguas y eliminarlas
                antiguas = Noticia.query.order_by(Noticia.fecha_hora.asc()).limit(
                    total_noticias - app.config.get('MAX_NEWS_COUNT', 30)
                ).all()

                for antigua in antiguas:
                    db.session.delete(antigua)

                db.session.commit()
                logger.info(f"🗑️ Eliminadas {len(antiguas)} noticias antiguas")

            logger.info(f"✅ Scraping completado: {nuevas} nuevas, {duplicadas} duplicadas")

        except Exception as e:
            logger.error(f"❌ Error en scraping: {e}")
            db.session.rollback()


@app.route('/')
def index():
    """
    Página principal - Lista de noticias
    """
    # Obtener las 30 últimas noticias ordenadas por fecha
    noticias = Noticia.query.order_by(Noticia.fecha_hora.desc()).limit(30).all()

    return render_template('index.html', noticias=noticias)


@app.route('/noticia/<int:noticia_id>')
def ver_noticia(noticia_id):
    """
    Ver detalle de una noticia
    """
    noticia = Noticia.query.get_or_404(noticia_id)
    return render_template('detalle.html', noticia=noticia)


@app.route('/apublicar')
def lista_apublicar():
    """
    Ver lista de noticias seleccionadas para publicar
    """
    noticias = APublicar.query.order_by(APublicar.selected_at.desc()).all()
    return render_template('apublicar.html', noticias=noticias)


@app.route('/apublicar/eliminar/<int:noticia_id>', methods=['POST'])
def eliminar_apublicar(noticia_id):
    """
    Eliminar una noticia de la lista A Publicar
    """
    try:
        noticia = APublicar.query.get_or_404(noticia_id)
        db.session.delete(noticia)
        db.session.commit()

        flash('✅ Noticia eliminada de "A Publicar"', 'success')
    except Exception as e:
        logger.error(f"Error eliminando noticia: {e}")
        flash('❌ Error al eliminar la noticia', 'error')
        db.session.rollback()

    return redirect(url_for('lista_apublicar'))


@app.route('/seleccionar', methods=['POST'])
def seleccionar_noticias():
    """
    Copiar noticias seleccionadas a la tabla APublicar
    """
    try:
        # Obtener IDs seleccionados del formulario
        noticias_ids = request.form.getlist('noticias_seleccionadas')

        if not noticias_ids:
            flash('No se seleccionaron noticias', 'warning')
            return redirect(url_for('index'))

        copiadas = 0
        ya_existentes = 0

        for noticia_id in noticias_ids:
            # Obtener la noticia original
            noticia = Noticia.query.get(int(noticia_id))
            if not noticia:
                continue

            # Verificar si ya existe en APublicar por URL
            existe = APublicar.query.filter_by(url=noticia.url).first()
            if existe:
                ya_existentes += 1
                continue

            # Copiar a APublicar
            a_publicar = APublicar(
                titulo=noticia.titulo,
                texto=noticia.texto,
                url=noticia.url,
                fecha_hora=noticia.fecha_hora,
                temas=noticia.temas,
                noticia_id=noticia.id
            )

            db.session.add(a_publicar)
            copiadas += 1

        db.session.commit()

        # Mensajes de feedback
        if copiadas > 0:
            flash(f'✅ {copiadas} noticia(s) copiada(s) a "A Publicar"', 'success')
        if ya_existentes > 0:
            flash(f'ℹ️ {ya_existentes} noticia(s) ya estaba(n) en "A Publicar"', 'info')

    except Exception as e:
        logger.error(f"Error seleccionando noticias: {e}")
        flash('❌ Error al copiar noticias', 'error')
        db.session.rollback()

    return redirect(url_for('index'))


@app.route('/scrape/manual')
def scrape_manual():
    """
    Ejecutar scraping manual
    """
    try:
        scrape_and_save_news()
        flash('✅ Scraping ejecutado correctamente', 'success')
    except Exception as e:
        logger.error(f"Error en scraping manual: {e}")
        flash(f'❌ Error en scraping: {str(e)}', 'error')

    return redirect(url_for('index'))


@app.route('/api/noticias')
def api_noticias():
    """
    API endpoint para obtener noticias en formato JSON
    """
    noticias = Noticia.query.order_by(Noticia.fecha_hora.desc()).limit(30).all()
    return jsonify([noticia.to_dict() for noticia in noticias])


@app.route('/api/apublicar')
def api_apublicar():
    """
    API endpoint para obtener noticias a publicar en formato JSON
    """
    noticias = APublicar.query.order_by(APublicar.selected_at.desc()).all()
    return jsonify([noticia.to_dict() for noticia in noticias])


@app.route('/apublicar/procesar/<int:noticia_id>', methods=['POST'])
def procesar_noticia(noticia_id):
    """
    Procesar una noticia individual para RRSS (traducción + optimización)
    """
    try:
        # Verificar que tengamos la API key de Anthropic
        anthropic_key = app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_key:
            flash('❌ API key de Anthropic no configurada', 'error')
            return redirect(url_for('lista_apublicar'))

        # Crear procesador
        processor = SocialMediaProcessor(anthropic_api_key=anthropic_key)

        # Procesar noticia
        success = processor.process_item(noticia_id)

        if success:
            flash('✅ Noticia procesada y traducida exitosamente', 'success')
        else:
            flash('❌ Error al procesar la noticia', 'error')

    except Exception as e:
        logger.error(f"Error procesando noticia {noticia_id}: {e}")
        flash(f'❌ Error: {str(e)}', 'error')

    return redirect(url_for('lista_apublicar'))


@app.route('/apublicar/procesar-todas', methods=['POST'])
def procesar_todas():
    """
    Procesar todas las noticias pendientes (no procesadas) para RRSS
    """
    try:
        # Verificar que tengamos la API key de Anthropic
        anthropic_key = app.config.get('ANTHROPIC_API_KEY')
        if not anthropic_key:
            flash('❌ API key de Anthropic no configurada', 'error')
            return redirect(url_for('lista_apublicar'))

        # Crear procesador
        processor = SocialMediaProcessor(anthropic_api_key=anthropic_key)

        # Obtener límite del request (opcional)
        limit = request.form.get('limit', type=int)

        # Procesar pendientes
        stats = processor.process_all_pending(limit=limit)

        # Mensaje de resultado
        msg = f"✅ Procesamiento completado: {stats['exitosos']} exitosos"
        if stats['fallidos'] > 0:
            msg += f", {stats['fallidos']} fallidos"
        if stats['ya_procesados'] > 0:
            msg += f", {stats['ya_procesados']} ya procesados"

        flash(msg, 'success' if stats['fallidos'] == 0 else 'warning')

    except Exception as e:
        logger.error(f"Error procesando todas las noticias: {e}")
        flash(f'❌ Error: {str(e)}', 'error')

    return redirect(url_for('lista_apublicar'))


@app.route('/api/export/social-media')
def export_social_media():
    """
    Exportar noticias procesadas en formato JSON para redes sociales

    Query params:
        - ids: Lista de IDs separados por coma (opcional)
        - platform: Plataforma específica (twitter, facebook, instagram, linkedin, whatsapp)
        - procesados: true/false - solo procesados o todos (default: true)
    """
    try:
        # Obtener parámetros
        ids_param = request.args.get('ids')
        platform = request.args.get('platform')
        solo_procesados = request.args.get('procesados', 'true').lower() == 'true'

        # Crear procesador
        anthropic_key = app.config.get('ANTHROPIC_API_KEY')
        processor = SocialMediaProcessor(anthropic_api_key=anthropic_key)

        # Construir query
        query = APublicar.query

        if solo_procesados:
            query = query.filter_by(procesado=True)

        if ids_param:
            # Parsear IDs
            try:
                item_ids = [int(id.strip()) for id in ids_param.split(',')]
                query = query.filter(APublicar.id.in_(item_ids))
            except ValueError:
                return jsonify({'error': 'IDs inválidos'}), 400

        items = query.all()

        if not items:
            return jsonify({
                'message': 'No hay noticias disponibles para exportar',
                'data': []
            }), 200

        # Exportar datos
        export_data = processor.export_for_social_media(
            item_ids=[item.id for item in items],
            platform=platform
        )

        # Metadata
        metadata = {
            'total': len(export_data),
            'generated_at': datetime.utcnow().isoformat(),
            'platform': platform or 'all',
            'procesados': solo_procesados
        }

        return jsonify({
            'metadata': metadata,
            'data': export_data
        }), 200

    except Exception as e:
        logger.error(f"Error exportando para RRSS: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats/processing')
def stats_processing():
    """
    Obtener estadísticas de procesamiento de RRSS
    """
    try:
        anthropic_key = app.config.get('ANTHROPIC_API_KEY')
        processor = SocialMediaProcessor(anthropic_api_key=anthropic_key)

        stats = processor.get_processing_stats()
        categories = processor.get_processed_by_category()

        return jsonify({
            'stats': stats,
            'categories': categories
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/news/to-publish', methods=['GET'])
@csrf.exempt
def api_news_to_publish():
    """
    API endpoint para que SocialPublisher obtenga noticias pendientes de publicar

    Query params:
        - procesados: true/false (default: true) - solo noticias procesadas
        - limit: int (default: 10) - cantidad máxima de noticias
    """
    try:
        # Parámetros
        solo_procesados = request.args.get('procesados', 'true').lower() == 'true'
        limit = request.args.get('limit', 10, type=int)

        # Query base
        query = APublicar.query.filter_by(publicado=False)

        if solo_procesados:
            query = query.filter_by(procesado=True)

        # Ordenar por fecha de selección y limitar
        noticias = query.order_by(APublicar.selected_at.asc()).limit(limit).all()

        return jsonify({
            'count': len(noticias),
            'noticias': [noticia.to_dict() for noticia in noticias]
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo noticias para publicar: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/news/<int:noticia_id>/mark-published', methods=['POST'])
@csrf.exempt
def api_mark_published(noticia_id):
    """
    Marcar una noticia como publicada en una plataforma específica

    Body JSON:
    {
        "platform": "linkedin",
        "post_id": "urn:li:share:123456",
        "post_url": "https://linkedin.com/...",
        "error": null  # opcional, si hubo error
    }
    """
    try:
        noticia = APublicar.query.get_or_404(noticia_id)
        data = request.get_json()

        if not data or 'platform' not in data:
            return jsonify({'error': 'platform es requerido'}), 400

        platform = data['platform']

        # Inicializar plataformas_publicadas si es None
        if noticia.plataformas_publicadas is None:
            noticia.plataformas_publicadas = {}

        # Si hubo error
        if data.get('error'):
            noticia.ultimo_error = f"{platform}: {data['error']}"
            noticia.intentos_publicacion = (noticia.intentos_publicacion or 0) + 1
            db.session.commit()

            return jsonify({
                'message': 'Error registrado',
                'noticia_id': noticia_id,
                'error': data['error']
            }), 200

        # Publicación exitosa
        noticia.plataformas_publicadas[platform] = {
            'post_id': data.get('post_id'),
            'post_url': data.get('post_url'),
            'published_at': datetime.utcnow().isoformat()
        }

        # Marcar como publicada si es la primera plataforma
        if not noticia.publicado:
            noticia.publicado = True
            noticia.published_at = datetime.utcnow()

        noticia.intentos_publicacion = (noticia.intentos_publicacion or 0) + 1
        noticia.ultimo_error = None  # Limpiar error previo

        db.session.commit()

        return jsonify({
            'message': 'Noticia marcada como publicada',
            'noticia_id': noticia_id,
            'platform': platform,
            'total_platforms': len(noticia.plataformas_publicadas)
        }), 200

    except Exception as e:
        logger.error(f"Error marcando noticia {noticia_id} como publicada: {e}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/news/<int:noticia_id>/publication-status', methods=['GET'])
def api_publication_status(noticia_id):
    """
    Obtener el estado de publicación de una noticia
    """
    try:
        noticia = APublicar.query.get_or_404(noticia_id)

        return jsonify({
            'noticia_id': noticia_id,
            'publicado': noticia.publicado,
            'plataformas': noticia.plataformas_publicadas or {},
            'intentos': noticia.intentos_publicacion or 0,
            'ultimo_error': noticia.ultimo_error,
            'published_at': noticia.published_at.isoformat() if noticia.published_at else None
        }), 200

    except Exception as e:
        logger.error(f"Error obteniendo estado de publicación: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """
    Health check endpoint
    """
    try:
        # Verificar conexión a BD
        db.session.execute(text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500


def init_scheduler():
    """
    Inicializa el scheduler para scraping automático
    """
    if not scheduler.running:
        # Agregar job de scraping
        interval_hours = app.config.get('SCRAPE_INTERVAL_HOURS', 24)
        scheduler.add_job(
            func=scrape_and_save_news,
            trigger='interval',
            hours=interval_hours,
            id='scrape_news',
            name='Scrape AI News',
            replace_existing=True
        )

        # Iniciar scheduler
        scheduler.start()
        logger.info(f"⏰ Scheduler iniciado - ejecutando cada {interval_hours} horas")


if __name__ == '__main__':
    # Inicializar scheduler
    init_scheduler()

    # Ejecutar un scraping inicial
    logger.info("🚀 Iniciando WebIAScrap...")
    scrape_and_save_news()

    # Ejecutar aplicación
    app.run(
        host=app.config.get('HOST', '0.0.0.0'),
        port=app.config.get('PORT', 8000),
        debug=app.config.get('DEBUG', False)
    )
