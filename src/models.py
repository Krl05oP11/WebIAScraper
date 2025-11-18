"""
Modelos de base de datos para WebIAScrap
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean

db = SQLAlchemy()


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
    temas = Column(String(500), nullable=True)  # 3-5 palabras separadas por comas
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
    temas = Column(String(500), nullable=True)
    noticia_id = Column(Integer, nullable=True)

    # Contenido traducido al español
    titulo_es = Column(String(500), nullable=True)
    texto_es = Column(Text, nullable=True)

    # Resúmenes para RRSS (en español)
    resumen_corto = Column(String(280), nullable=True)  # Twitter/LinkedIn
    resumen_medio = Column(String(500), nullable=True)  # Facebook
    resumen_largo = Column(Text, nullable=True)  # Instagram/Blog

    # Metadata para RRSS
    hashtags = Column(String(500), nullable=True)  # Hashtags separados por comas
    categoria = Column(String(100), nullable=True)  # Tutorial, Research, Tools, etc.
    procesado = Column(Boolean, default=False)  # Si ya fue procesado por Claude

    # Timestamps
    selected_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)  # Cuando fue procesado

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
            'selected_at': self.selected_at.isoformat() if self.selected_at else None,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None
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
            'temas': self.temas.split(',') if self.temas else [],
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
