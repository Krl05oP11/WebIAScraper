"""
Tests para el web scraper
"""
import pytest
from datetime import datetime
import sys
sys.path.insert(0, '/app')

from src.news_scraper import NewsScraper


def test_scraper_initialization():
    """Test inicialización del scraper"""
    scraper = NewsScraper(
        api_key="test_key",
        keywords=["AI", "machine learning"],
        sources=["techcrunch"]
    )

    assert scraper.api_key == "test_key"
    assert "AI" in scraper.keywords
    assert "techcrunch" in scraper.sources


def test_scraper_sin_api_key():
    """Test que falle sin API key"""
    with pytest.raises(ValueError, match="NewsAPI key es requerida"):
        NewsScraper(api_key="", keywords=["AI"])


def test_parse_date():
    """Test parseo de fechas"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    # Fecha válida en formato ISO
    date_str = "2024-01-15T10:30:00Z"
    parsed_date = scraper._parse_date(date_str)

    assert isinstance(parsed_date, datetime)
    assert parsed_date.day == 15
    assert parsed_date.month == 1


def test_parse_date_invalida():
    """Test parseo de fecha inválida"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    # Fecha inválida debería retornar fecha actual
    parsed_date = scraper._parse_date("invalid-date")

    assert isinstance(parsed_date, datetime)


def test_create_summary():
    """Test creación de resúmenes"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    descripcion = "Esta es una descripción de prueba."
    contenido = "Este es el contenido del artículo de prueba."

    summary = scraper._create_summary(descripcion, contenido)

    assert "descripción" in summary
    assert "contenido" in summary


def test_create_summary_max_words():
    """Test límite de palabras en resumen"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    # Crear texto largo
    descripcion = " ".join(["palabra"] * 500)
    contenido = " ".join(["texto"] * 600)

    summary = scraper._create_summary(descripcion, contenido, max_words=100)

    # Verificar que está limitado
    word_count = len(summary.split())
    assert word_count <= 101  # +1 por si hay "..." al final


def test_extract_topics():
    """Test extracción de temas"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    titulo = "Machine Learning and AI Revolutionize Data Science"
    texto = "Artificial intelligence and machine learning are transforming data science..."

    temas = scraper._extract_topics(titulo, texto)

    # Debe encontrar keywords relevantes
    assert len(temas) > 0
    assert any(keyword in temas.lower() for keyword in ['ai', 'machine learning', 'data science'])


def test_extract_topics_sin_keywords():
    """Test extracción cuando no hay keywords técnicas"""
    scraper = NewsScraper(api_key="test_key", keywords=["AI"])

    titulo = "Random Article About Nothing"
    texto = "This is just some random text without technical keywords"

    temas = scraper._extract_topics(titulo, texto)

    # Debe retornar al menos algunos temas
    assert len(temas) > 0
