"""
Modelos de base de datos para WebIAScrap
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import ARRAY

db = SQLAlchemy()


class StringArray(TypeDecorator):
    """
    Tipo personalizado que maneja arrays de strings en PostgreSQL
    y strings separados por comas en SQLite para compatibilidad.
    """
    impl = String(500)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(ARRAY(String))
        else:
            return dialect.type_descriptor(String(500))

    def process_bind_param(self, value, dialect):
        """Convierte lista a formato apropiado para cada BD"""
        if value is None:
            return value
        if dialect.name == 'postgresql':
            # PostgreSQL espera lista directamente
            return value if isinstance(value, list) else []
        else:
            # SQLite: convertir lista a string separado por comas
            if isinstance(value, list):
                return ', '.join(value)
            return value

    def process_result_value(self, value, dialect):
        """Convierte valor de BD a lista de Python"""
        if value is None:
            return []
        if isinstance(value, list):
            return value
        # Si es string (SQLite), convertir a lista
        if isinstance(value, str):
            return [item.strip() for item in value.split(',') if item.strip()]
        return []


class Noticia(db.Model):
    """
    Tabla principal para almacenar noticias scrapeadas
    """
    __tablename__ = 'noticias'

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(500), nullable=False)
    texto = Column(Text, nullable=False)  # Resumen hasta 1000 palabras
    url = Column(String(1000), nullable=False, unique=True)
    fecha_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    temas = Column(StringArray, nullable=True)  # Lista de 3-5 temas (array en PostgreSQL, string en SQLite)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Noticia {self.id}: {self.titulo[:50]}>'

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'texto': self.texto,
            'url': self.url,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'temas': self.temas,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class APublicar(db.Model):
    """
    Tabla para almacenar noticias seleccionadas por el usuario para publicar
    Con procesamiento para RRSS incluido
    """
    __tablename__ = 'apublicar'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Contenido original
    titulo = Column(String(500), nullable=False)
    texto = Column(Text, nullable=False)
    url = Column(String(1000), nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    temas = Column(StringArray, nullable=True)  # Lista de temas (array en PostgreSQL, string en SQLite)
    noticia_id = Column(Integer, nullable=True)

    # Contenido traducido al español
    titulo_es = Column(String(500), nullable=True)
    texto_es = Column(Text, nullable=True)

    # Resúmenes para RRSS (en español)
    resumen_corto = Column(String(280), nullable=True)  # Twitter/LinkedIn
    resumen_medio = Column(String(1000), nullable=True)  # Facebook
    resumen_largo = Column(Text, nullable=True)  # Instagram/Blog

    # Metadata para RRSS
    hashtags = Column(String(500), nullable=True)  # Hashtags separados por comas
    categoria = Column(String(100), nullable=True)  # Tutorial, Research, Tools, etc.
    procesado = Column(Boolean, default=False)  # Si ya fue procesado por Claude

    # Tracking de publicación en redes sociales
    publicado = Column(Boolean, default=False)  # Si ya fue publicada en al menos una plataforma
    plataformas_seleccionadas = Column(JSON, nullable=True)  # ["telegram", "bluesky", "twitter", "linkedin"] - Plataformas elegidas por el usuario
    plataformas_publicadas = Column(JSON, nullable=True)  # {"linkedin": {"post_id": "...", "url": "...", "published_at": "...", "intentos": 0}}
    intentos_publicacion = Column(Integer, default=0)  # Contador de intentos de publicación GLOBAL (deprecated - usar plataformas_publicadas)
    ultimo_error = Column(Text, nullable=True)  # Último error de publicación si hubo

    # Nuevos campos para flujo mejorado
    fase = Column(String(50), default='pendiente')  # pendiente, procesando, procesado, publicando, publicado_parcial, publicado_completo, fallido
    contador_reintentos = Column(Integer, default=0)  # Reintentos automáticos realizados (máx 3)
    ultimo_intento = Column(DateTime, nullable=True)  # Timestamp del último intento de publicación
    proximo_reintento = Column(DateTime, nullable=True)  # Timestamp del próximo reintento automático

    # Timestamps
    selected_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)  # Cuando fue procesado
    published_at = Column(DateTime, nullable=True)  # Primera publicación exitosa
    expires_at = Column(DateTime, nullable=True)  # Fecha de expiración (selected_at + 2 días)

    def __repr__(self):
        return f'<APublicar {self.id}: {self.titulo[:50]}>'

    def to_dict(self):
        """Convierte el objeto a diccionario"""
        return {
            'id': self.id,
            'titulo': self.titulo,
            'texto': self.texto,
            'url': self.url,
            'fecha_hora': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'temas': self.temas,
            'noticia_id': self.noticia_id,
            'titulo_es': self.titulo_es,
            'texto_es': self.texto_es,
            'resumen_corto': self.resumen_corto,
            'resumen_medio': self.resumen_medio,
            'resumen_largo': self.resumen_largo,
            'hashtags': self.hashtags,
            'categoria': self.categoria,
            'procesado': self.procesado,
            'publicado': self.publicado,
            'plataformas_seleccionadas': self.plataformas_seleccionadas,
            'plataformas_publicadas': self.plataformas_publicadas,
            'intentos_publicacion': self.intentos_publicacion,
            'ultimo_error': self.ultimo_error,
            'fase': self.fase,
            'contador_reintentos': self.contador_reintentos,
            'ultimo_intento': self.ultimo_intento.isoformat() if self.ultimo_intento else None,
            'proximo_reintento': self.proximo_reintento.isoformat() if self.proximo_reintento else None,
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

    def to_social_media_json(self):
        """
        Formato optimizado para APIs de redes sociales
        """
        return {
            'id': self.id,
            'titulo_original': self.titulo,
            'titulo_es': self.titulo_es,
            'url': self.url,
            'fecha_publicacion': self.fecha_hora.isoformat() if self.fecha_hora else None,
            'categoria': self.categoria,
            'contenido': {
                'twitter_linkedin': self.resumen_corto,
                'facebook': self.resumen_medio,
                'instagram_whatsapp': self.resumen_largo
            },
            'hashtags': self.hashtags.split(',') if self.hashtags else [],
            'temas': self.temas if self.temas else [],  # temas ya es una lista
            'idioma': 'es',
            'preparado_para_publicacion': self.procesado
        }


def init_db(app):
    """
    Inicializa la base de datos
    """
    db.init_app(app)

    with app.app_context():
        # Crear todas las tablas
        db.create_all()
        print("✅ Base de datos inicializada correctamente")
