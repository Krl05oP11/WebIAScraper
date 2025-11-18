"""
Web Scraper para noticias de IA usando NewsAPI
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from newsapi import NewsApiClient
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

logger = logging.getLogger(__name__)


class NewsScraper:
    """
    Scraper de noticias usando NewsAPI
    """

    def __init__(self, api_key: str, keywords: List[str], sources: List[str] = None):
        """
        Inicializa el scraper

        Args:
            api_key: API key de NewsAPI
            keywords: Lista de palabras clave para buscar
            sources: Lista de fuentes de noticias (opcional)
        """
        if not api_key:
            raise ValueError("NewsAPI key es requerida")

        self.api_key = api_key
        self.keywords = keywords
        self.sources = sources
        self.client = NewsApiClient(api_key=api_key)

        # Cargar stopwords para extracción de temas
        try:
            self.stop_words = set(stopwords.words('english'))
        except LookupError:
            logger.warning("Stopwords no disponibles, usando set vacío")
            self.stop_words = set()

    def fetch_news(self, max_results: int = 30) -> List[Dict]:
        """
        Obtiene noticias desde NewsAPI

        Args:
            max_results: Número máximo de noticias a obtener

        Returns:
            Lista de diccionarios con noticias
        """
        all_articles = []

        try:
            # Buscar por cada keyword
            for keyword in self.keywords:
                keyword = keyword.strip()
                logger.info(f"Buscando noticias para: {keyword}")

                # Buscar noticias de los últimos 7 días
                from_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

                # Realizar búsqueda
                response = self.client.get_everything(
                    q=keyword,
                    sources=','.join(self.sources) if self.sources else None,
                    from_param=from_date,
                    language='en',
                    sort_by='publishedAt',
                    page_size=min(100, max_results)
                )

                if response.get('status') == 'ok':
                    articles = response.get('articles', [])
                    logger.info(f"Encontradas {len(articles)} noticias para '{keyword}'")
                    all_articles.extend(articles)
                else:
                    logger.error(f"Error en respuesta de NewsAPI: {response}")

            # Procesar y formatear artículos
            processed_news = self._process_articles(all_articles, max_results)

            logger.info(f"Total de noticias procesadas: {len(processed_news)}")
            return processed_news

        except Exception as e:
            logger.error(f"Error al obtener noticias: {str(e)}")
            return []

    def _process_articles(self, articles: List[Dict], max_results: int) -> List[Dict]:
        """
        Procesa y formatea los artículos de NewsAPI

        Args:
            articles: Lista de artículos de NewsAPI
            max_results: Número máximo de resultados

        Returns:
            Lista de noticias procesadas
        """
        processed = []
        seen_urls = set()

        # Ordenar por fecha de publicación (más recientes primero)
        articles = sorted(
            articles,
            key=lambda x: x.get('publishedAt', ''),
            reverse=True
        )

        for article in articles:
            # Evitar duplicados por URL
            url = article.get('url', '')
            if url in seen_urls or not url:
                continue

            seen_urls.add(url)

            # Extraer y procesar información
            titulo = article.get('title', 'Sin título')
            descripcion = article.get('description', '')
            contenido = article.get('content', '')

            # Crear texto combinando descripción y contenido (máximo 1000 palabras)
            texto = self._create_summary(descripcion, contenido)

            # Parsear fecha
            fecha_hora = self._parse_date(article.get('publishedAt'))

            # Extraer temas/keywords del contenido
            temas = self._extract_topics(titulo, texto)

            processed.append({
                'titulo': titulo[:500],  # Limitar a 500 caracteres
                'texto': texto,
                'url': url[:1000],  # Limitar a 1000 caracteres
                'fecha_hora': fecha_hora,
                'temas': temas
            })

            # Limitar al número máximo de resultados
            if len(processed) >= max_results:
                break

        return processed

    def _create_summary(self, descripcion: str, contenido: str, max_words: int = 1000) -> str:
        """
        Crea un resumen combinando descripción y contenido

        Args:
            descripcion: Descripción del artículo
            contenido: Contenido del artículo
            max_words: Número máximo de palabras

        Returns:
            Resumen del artículo
        """
        # Combinar descripción y contenido
        texto = f"{descripcion or ''} {contenido or ''}".strip()

        # Dividir en palabras y limitar
        palabras = texto.split()
        if len(palabras) > max_words:
            palabras = palabras[:max_words]
            texto = ' '.join(palabras) + '...'
        else:
            texto = ' '.join(palabras)

        return texto if texto else 'Sin contenido disponible'

    def _parse_date(self, date_str: Optional[str]) -> datetime:
        """
        Parsea la fecha de publicación

        Args:
            date_str: String de fecha en formato ISO

        Returns:
            Objeto datetime
        """
        if not date_str:
            return datetime.utcnow()

        try:
            # NewsAPI devuelve fechas en formato ISO 8601
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.warning(f"Error parseando fecha '{date_str}': {e}")
            return datetime.utcnow()

    def _extract_topics(self, titulo: str, texto: str, max_topics: int = 5) -> str:
        """
        Extrae temas principales del artículo usando análisis simple de keywords

        Args:
            titulo: Título del artículo
            texto: Texto del artículo
            max_topics: Número máximo de temas a extraer

        Returns:
            String con temas separados por comas
        """
        # Combinar título y texto (el título tiene más peso)
        combined_text = f"{titulo} {titulo} {texto}".lower()

        # Palabras técnicas relevantes de IA/ML
        ai_keywords = {
            'ai', 'artificial intelligence', 'machine learning', 'deep learning',
            'neural network', 'nlp', 'computer vision', 'robotics',
            'data science', 'algorithm', 'chatbot', 'llm', 'gpt',
            'transformer', 'bert', 'tensorflow', 'pytorch', 'openai',
            'anthropic', 'claude', 'chatgpt', 'generative', 'model'
        }

        # Buscar keywords relevantes
        found_topics = []
        for keyword in ai_keywords:
            if keyword in combined_text:
                # Capitalizar primera letra de cada palabra
                topic = ' '.join(word.capitalize() for word in keyword.split())
                if topic not in found_topics:
                    found_topics.append(topic)

            if len(found_topics) >= max_topics:
                break

        # Si no se encontraron suficientes keywords técnicas, extraer palabras importantes
        if len(found_topics) < 3:
            words = re.findall(r'\b[a-z]{4,}\b', combined_text)
            word_freq = {}

            for word in words:
                if word not in self.stop_words and word not in ['http', 'https', 'www']:
                    word_freq[word] = word_freq.get(word, 0) + 1

            # Ordenar por frecuencia
            sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

            # Agregar palabras más frecuentes
            for word, _ in sorted_words[:max_topics - len(found_topics)]:
                found_topics.append(word.capitalize())

        # Asegurar que tengamos al menos algunos temas
        if not found_topics:
            found_topics = ['AI', 'Technology', 'News']

        return ', '.join(found_topics[:max_topics])


def test_scraper(api_key: str):
    """
    Función de prueba del scraper

    Args:
        api_key: API key de NewsAPI
    """
    keywords = ['artificial intelligence', 'machine learning']
    sources = ['techcrunch', 'wired', 'the-verge']

    scraper = NewsScraper(api_key, keywords, sources)
    noticias = scraper.fetch_news(max_results=5)

    print(f"\n{'='*80}")
    print(f"NOTICIAS ENCONTRADAS: {len(noticias)}")
    print(f"{'='*80}\n")

    for i, noticia in enumerate(noticias, 1):
        print(f"{i}. {noticia['titulo']}")
        print(f"   URL: {noticia['url']}")
        print(f"   Fecha: {noticia['fecha_hora']}")
        print(f"   Temas: {noticia['temas']}")
        print(f"   Texto: {noticia['texto'][:100]}...")
        print()
