"""
Scraper de fuentes técnicas especializadas en IA/ML usando RSS/Atom feeds
"""
import logging
import feedparser
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class TechnicalSourcesScraper:
    """
    Scraper para fuentes técnicas especializadas en IA, Machine Learning y Data Science
    """

    # Fuentes RSS técnicas
    TECHNICAL_SOURCES = {
        'huggingface': {
            'name': 'Hugging Face Blog',
            'rss_url': 'https://huggingface.co/blog/feed.xml',
            'tipo': 'Research/Tools'
        },
        'arxiv_ai': {
            'name': 'ArXiv - Artificial Intelligence',
            'rss_url': 'http://export.arxiv.org/rss/cs.AI',
            'tipo': 'Research'
        },
        'arxiv_ml': {
            'name': 'ArXiv - Machine Learning',
            'rss_url': 'http://export.arxiv.org/rss/cs.LG',
            'tipo': 'Research'
        },
        'google_ai': {
            'name': 'Google AI Blog',
            'rss_url': 'https://blog.research.google/feeds/posts/default',
            'tipo': 'Research/News'
        },
        'deepmind': {
            'name': 'DeepMind Blog',
            'rss_url': 'https://deepmind.google/blog/rss.xml',
            'tipo': 'Research'
        },
        'openai': {
            'name': 'OpenAI Blog',
            'rss_url': 'https://openai.com/blog/rss.xml',
            'tipo': 'Research/News'
        },
        'distill': {
            'name': 'Distill.pub',
            'rss_url': 'https://distill.pub/rss.xml',
            'tipo': 'Research'
        },
        'ml_mastery': {
            'name': 'Machine Learning Mastery',
            'rss_url': 'https://machinelearningmastery.com/feed/',
            'tipo': 'Tutorial'
        },
        'towards_ai': {
            'name': 'Towards AI',
            'rss_url': 'https://pub.towardsai.net/feed',
            'tipo': 'Tutorial/News'
        },
        # Nuevas fuentes agregadas 22 dic 2025
        'mit_tech_ai': {
            'name': 'MIT Technology Review - AI',
            'rss_url': 'https://www.technologyreview.com/topic/artificial-intelligence/feed',
            'tipo': 'News/Analysis'
        },
        'wired_ai': {
            'name': 'WIRED - AI',
            'rss_url': 'https://www.wired.com/feed/tag/ai/latest/rss',
            'tipo': 'News/Analysis'
        },
        'kdnuggets': {
            'name': 'KDnuggets',
            'rss_url': 'https://www.kdnuggets.com/feed',
            'tipo': 'Tutorial/News'
        },
        'towards_data_science': {
            'name': 'Towards Data Science',
            'rss_url': 'https://towardsdatascience.com/feed',
            'tipo': 'Tutorial/Analysis'
        },
        'analytics_vidhya': {
            'name': 'Analytics Vidhya',
            'rss_url': 'https://www.analyticsvidhya.com/feed/',
            'tipo': 'Tutorial/News'
        },
        'langchain_blog': {
            'name': 'LangChain Blog',
            'rss_url': 'https://blog.langchain.dev/rss/',
            'tipo': 'Tools/Framework'
        },
        'llamaindex_blog': {
            'name': 'LlamaIndex Blog',
            'rss_url': 'https://www.llamaindex.ai/blog/rss.xml',
            'tipo': 'Tools/Framework'
        },
        'the_batch': {
            'name': 'The Batch (DeepLearning.AI)',
            'rss_url': 'https://www.deeplearning.ai/the-batch/feed/',
            'tipo': 'Newsletter/News'
        },
        'science_news_ai': {
            'name': 'Science News - AI',
            'rss_url': 'https://www.sciencenews.org/topic/artificial-intelligence/feed',
            'tipo': 'News/Research'
        }
    }

    def __init__(self, sources: Optional[List[str]] = None, days_back: int = 7):
        """
        Inicializa el scraper de fuentes técnicas

        Args:
            sources: Lista de IDs de fuentes a scrapear (None = todas)
            days_back: Días hacia atrás para buscar artículos
        """
        self.sources = sources or list(self.TECHNICAL_SOURCES.keys())
        self.days_back = days_back
        self.cutoff_date = datetime.now() - timedelta(days=days_back)

    def fetch_all_sources(self, max_per_source: int = 10) -> List[Dict]:
        """
        Obtiene artículos de todas las fuentes configuradas

        Args:
            max_per_source: Máximo de artículos por fuente

        Returns:
            Lista de diccionarios con artículos
        """
        all_articles = []

        for source_id in self.sources:
            if source_id not in self.TECHNICAL_SOURCES:
                logger.warning(f"Fuente desconocida: {source_id}")
                continue

            source_info = self.TECHNICAL_SOURCES[source_id]
            logger.info(f"Scrapeando: {source_info['name']}")

            try:
                articles = self._fetch_rss_feed(
                    source_info['rss_url'],
                    source_info['name'],
                    source_info['tipo'],
                    max_per_source
                )
                all_articles.extend(articles)
                logger.info(f"  ✓ {len(articles)} artículos obtenidos de {source_info['name']}")

            except Exception as e:
                logger.error(f"  ✗ Error scrapeando {source_info['name']}: {e}")
                continue

        # Eliminar duplicados por URL
        seen_urls = set()
        unique_articles = []

        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)

        # Ordenar por fecha (más recientes primero)
        unique_articles.sort(key=lambda x: x['fecha_hora'], reverse=True)

        logger.info(f"Total de artículos únicos: {len(unique_articles)}")
        return unique_articles

    def _fetch_rss_feed(
        self,
        feed_url: str,
        source_name: str,
        tipo: str,
        max_articles: int
    ) -> List[Dict]:
        """
        Obtiene artículos de un feed RSS/Atom

        Args:
            feed_url: URL del feed RSS
            source_name: Nombre de la fuente
            tipo: Tipo de contenido (Research, Tutorial, etc.)
            max_articles: Máximo de artículos a obtener

        Returns:
            Lista de artículos procesados
        """
        try:
            # Parsear el feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed mal formado: {feed_url} - {feed.bozo_exception}")

            articles = []

            for entry in feed.entries[:max_articles * 2]:  # Obtener más para filtrar por fecha
                # Parsear fecha de publicación
                fecha_hora = self._parse_feed_date(entry)

                # Filtrar artículos antiguos
                if fecha_hora < self.cutoff_date:
                    continue

                # Extraer información
                titulo = entry.get('title', 'Sin título').strip()
                url = entry.get('link', '')

                # Obtener resumen/descripción
                texto = self._extract_description(entry)

                # Extraer temas del feed
                temas = self._extract_feed_topics(entry, tipo)

                # Agregar artículo
                articles.append({
                    'titulo': titulo[:500],
                    'texto': texto,
                    'url': url[:1000],
                    'fecha_hora': fecha_hora,
                    'temas': temas,
                    'fuente': source_name
                })

                if len(articles) >= max_articles:
                    break

            return articles

        except Exception as e:
            logger.error(f"Error procesando feed {feed_url}: {e}")
            return []

    def _parse_feed_date(self, entry: Dict) -> datetime:
        """
        Parsea la fecha de publicación de una entrada de feed

        Args:
            entry: Entrada del feed

        Returns:
            Objeto datetime
        """
        # Intentar diferentes campos de fecha
        date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']

        for field in date_fields:
            if hasattr(entry, field):
                time_struct = getattr(entry, field)
                if time_struct:
                    try:
                        return datetime(*time_struct[:6])
                    except Exception:
                        pass

        # Si no hay fecha válida, usar fecha actual
        return datetime.now()

    def _extract_description(self, entry: Dict) -> str:
        """
        Extrae y limpia la descripción/contenido de una entrada

        Args:
            entry: Entrada del feed

        Returns:
            Texto limpio del artículo
        """
        # Intentar diferentes campos de contenido
        content = ''

        if hasattr(entry, 'summary'):
            content = entry.summary
        elif hasattr(entry, 'description'):
            content = entry.description
        elif hasattr(entry, 'content'):
            if isinstance(entry.content, list) and len(entry.content) > 0:
                content = entry.content[0].get('value', '')
            else:
                content = str(entry.content)

        # Limpiar HTML
        if content:
            content = self._clean_html(content)

        # Limitar a 1000 palabras
        palabras = content.split()
        if len(palabras) > 1000:
            content = ' '.join(palabras[:1000]) + '...'

        return content if content else 'Sin contenido disponible'

    def _clean_html(self, html_text: str) -> str:
        """
        Limpia tags HTML del texto

        Args:
            html_text: Texto con HTML

        Returns:
            Texto limpio
        """
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)

            # Limpiar espacios múltiples
            text = re.sub(r'\s+', ' ', text)

            return text.strip()

        except Exception:
            # Si falla el parsing, intentar limpieza básica
            text = re.sub(r'<[^>]+>', '', html_text)
            text = re.sub(r'\s+', ' ', text)
            return text.strip()

    def _extract_feed_topics(self, entry: Dict, tipo: str) -> str:
        """
        Extrae temas de una entrada de feed

        Args:
            entry: Entrada del feed
            tipo: Tipo de fuente

        Returns:
            String con temas separados por comas
        """
        topics = []

        # Agregar tipo de fuente como primer tema
        topics.append(tipo)

        # Extraer tags/categorías del feed
        if hasattr(entry, 'tags'):
            for tag in entry.tags[:3]:
                tag_name = tag.get('term', '').strip()
                if tag_name and tag_name not in topics:
                    topics.append(tag_name.title())

        # Extraer keywords técnicas del título
        titulo = entry.get('title', '').lower()

        ai_keywords = {
            'llm': 'LLM',
            'gpt': 'GPT',
            'transformer': 'Transformers',
            'bert': 'BERT',
            'pytorch': 'PyTorch',
            'tensorflow': 'TensorFlow',
            'neural': 'Neural Networks',
            'deep learning': 'Deep Learning',
            'machine learning': 'Machine Learning',
            'computer vision': 'Computer Vision',
            'nlp': 'NLP',
            'reinforcement learning': 'Reinforcement Learning',
            'gan': 'GAN',
            'diffusion': 'Diffusion Models',
            'stable diffusion': 'Stable Diffusion',
            'dalle': 'DALL-E',
            'chatgpt': 'ChatGPT',
            'claude': 'Claude',
            'anthropic': 'Anthropic',
            'openai': 'OpenAI',
            'hugging face': 'Hugging Face'
        }

        for keyword, topic in ai_keywords.items():
            if keyword in titulo and topic not in topics:
                topics.append(topic)
                if len(topics) >= 5:
                    break

        # Asegurar al menos 3 temas
        if len(topics) < 3:
            topics.extend(['AI', 'Machine Learning', 'Technology'][:3 - len(topics)])

        return ', '.join(topics[:5])

    def get_source_names(self) -> List[str]:
        """
        Retorna la lista de nombres de fuentes disponibles

        Returns:
            Lista de nombres de fuentes
        """
        return [info['name'] for info in self.TECHNICAL_SOURCES.values()]


def test_technical_scraper():
    """
    Función de prueba del scraper técnico
    """
    # Probar con algunas fuentes
    test_sources = ['huggingface', 'arxiv_ai', 'google_ai']

    scraper = TechnicalSourcesScraper(sources=test_sources, days_back=30)
    articles = scraper.fetch_all_sources(max_per_source=5)

    print(f"\n{'='*100}")
    print(f"ARTÍCULOS TÉCNICOS ENCONTRADOS: {len(articles)}")
    print(f"{'='*100}\n")

    for i, article in enumerate(articles, 1):
        print(f"{i}. {article['titulo']}")
        print(f"   Fuente: {article['fuente']}")
        print(f"   URL: {article['url']}")
        print(f"   Fecha: {article['fecha_hora'].strftime('%Y-%m-%d %H:%M')}")
        print(f"   Temas: {article['temas']}")
        print(f"   Texto: {article['texto'][:150]}...")
        print()


if __name__ == '__main__':
    # Configurar logging para pruebas
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    test_technical_scraper()
