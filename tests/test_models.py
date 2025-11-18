"""
Tests para modelos de base de datos
"""
import pytest
from datetime import datetime
import sys
sys.path.insert(0, '/app')

from src.models import db, Noticia, APublicar


def test_crear_noticia(app):
    """Test crear una noticia"""
    with app.app_context():
        noticia = Noticia(
            titulo="Test Noticia",
            texto="Contenido de prueba",
            url="https://ejemplo.com/test",
            fecha_hora=datetime.utcnow(),
            temas="AI, ML, Test"
        )

        db.session.add(noticia)
        db.session.commit()

        # Verificar que se guardó
        assert noticia.id is not None
        assert noticia.titulo == "Test Noticia"


def test_noticia_to_dict(app):
    """Test conversión de noticia a diccionario"""
    with app.app_context():
        noticia = Noticia(
            titulo="Test Dict",
            texto="Contenido",
            url="https://test.com",
            fecha_hora=datetime.utcnow(),
            temas="Test"
        )

        noticia_dict = noticia.to_dict()

        assert 'titulo' in noticia_dict
        assert 'texto' in noticia_dict
        assert 'url' in noticia_dict
        assert noticia_dict['titulo'] == "Test Dict"


def test_crear_apublicar(app):
    """Test crear entrada en APublicar"""
    with app.app_context():
        publicar = APublicar(
            titulo="Test Publicar",
            texto="Contenido para publicar",
            url="https://ejemplo.com/publicar",
            fecha_hora=datetime.utcnow(),
            temas="Test, Publicar",
            noticia_id=1
        )

        db.session.add(publicar)
        db.session.commit()

        assert publicar.id is not None
        assert publicar.titulo == "Test Publicar"
        assert publicar.noticia_id == 1


def test_url_unica_noticia(app):
    """Test que las URLs sean únicas en noticias"""
    with app.app_context():
        # Crear primera noticia
        noticia1 = Noticia(
            titulo="Noticia 1",
            texto="Contenido 1",
            url="https://ejemplo.com/unica",
            fecha_hora=datetime.utcnow(),
            temas="Test"
        )
        db.session.add(noticia1)
        db.session.commit()

        # Intentar crear noticia duplicada
        noticia2 = Noticia(
            titulo="Noticia 2",
            texto="Contenido 2",
            url="https://ejemplo.com/unica",  # Misma URL
            fecha_hora=datetime.utcnow(),
            temas="Test"
        )
        db.session.add(noticia2)

        # Debería fallar por URL duplicada
        with pytest.raises(Exception):
            db.session.commit()

        db.session.rollback()


@pytest.fixture
def app():
    """Crear aplicación de prueba"""
    from flask import Flask
    from config.settings import TestingConfig

    app = Flask(__name__)
    app.config.from_object(TestingConfig)

    from src.models import init_db
    init_db(app)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
