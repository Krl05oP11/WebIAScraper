"""
Servicio de traducción y optimización de contenido usando Claude API
"""
import os
import logging
from typing import Dict, List, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)


class TranslationService:
    """
    Servicio para traducir noticias de inglés a español y generar
    contenido optimizado para redes sociales usando Claude API
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el servicio de traducción

        Args:
            api_key: API key de Anthropic (si no se provee, usa variable de entorno)
        """
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Se requiere ANTHROPIC_API_KEY en .env o como parámetro")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-5"  # Claude Sonnet 4.5

    def translate_and_optimize(self, titulo: str, texto: str, url: str) -> Dict[str, str]:
        """
        Traduce el contenido al español y genera variantes para RRSS

        Args:
            titulo: Título original en inglés
            texto: Texto/resumen original en inglés
            url: URL de la noticia (para contexto)

        Returns:
            Diccionario con:
                - titulo_es: Título traducido
                - texto_es: Texto traducido completo
                - resumen_corto: 280 caracteres max (Twitter/LinkedIn)
                - resumen_medio: 500 caracteres max (Facebook)
                - resumen_largo: Texto más extenso (Instagram/WhatsApp)
                - hashtags: Hashtags relevantes separados por coma
                - categoria: Categoría del contenido
        """
        prompt = self._build_translation_prompt(titulo, texto, url)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,  # Temperatura baja para traducciones más precisas
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extraer el contenido de la respuesta
            content = response.content[0].text

            # Parsear la respuesta estructurada
            result = self._parse_response(content)

            logger.info(f"Traducción completada para: {titulo[:50]}...")
            return result

        except Exception as e:
            logger.error(f"Error en traducción: {e}")
            # Retornar estructura vacía en caso de error
            return {
                'titulo_es': titulo,
                'texto_es': texto,
                'resumen_corto': texto[:280],
                'resumen_medio': texto[:500],
                'resumen_largo': texto,
                'hashtags': '',
                'categoria': 'General'
            }

    def _build_translation_prompt(self, titulo: str, texto: str, url: str) -> str:
        """
        Construye el prompt para Claude con instrucciones específicas
        """
        return f"""Eres un experto en traducción técnica de contenido sobre Inteligencia Artificial y ciencia de datos.

Tu tarea es traducir el siguiente artículo de inglés a español y generar contenido optimizado para redes sociales.

**ARTÍCULO ORIGINAL:**
Título: {titulo}
URL: {url}
Contenido: {texto}

**INSTRUCCIONES:**

1. **Traducción al español:**
   - Traduce el título y contenido manteniendo la precisión técnica
   - Usa terminología técnica en español (ej: "aprendizaje automático", "redes neuronales")
   - Mantén los nombres propios de herramientas/frameworks en inglés (TensorFlow, PyTorch, etc.)

2. **Categorización:**
   - Determina la categoría del artículo: Tutorial, Research, Tools, Case Study, News, Opinion, o General
   - Base tu decisión en el contenido y enfoque del artículo

3. **Resúmenes para RRSS:**
   - **Resumen Corto** (máximo 280 caracteres): Para Twitter/LinkedIn. Debe ser impactante y conciso.
   - **Resumen Medio** (máximo 500 caracteres): Para Facebook. Más contexto pero aún breve.
   - **Resumen Largo** (800-1000 caracteres): Para Instagram/WhatsApp/Blog. Explicación más detallada.

4. **Hashtags:**
   - Genera 5-8 hashtags relevantes en español
   - Incluye hashtags generales (#IA, #MachineLearning) y específicos del tema
   - Usa CamelCase para mejor legibilidad

**FORMATO DE RESPUESTA:**
Devuelve EXACTAMENTE en este formato (respeta las etiquetas):

[TITULO_ES]
Título traducido aquí
[/TITULO_ES]

[TEXTO_ES]
Texto completo traducido aquí
[/TEXTO_ES]

[RESUMEN_CORTO]
Resumen de máximo 280 caracteres
[/RESUMEN_CORTO]

[RESUMEN_MEDIO]
Resumen de máximo 500 caracteres
[/RESUMEN_MEDIO]

[RESUMEN_LARGO]
Resumen extenso de 800-1000 caracteres
[/RESUMEN_LARGO]

[HASHTAGS]
#Hashtag1, #Hashtag2, #Hashtag3, etc
[/HASHTAGS]

[CATEGORIA]
Categoría (una sola palabra)
[/CATEGORIA]

Procede con la traducción y optimización:"""

    def _parse_response(self, content: str) -> Dict[str, str]:
        """
        Parsea la respuesta estructurada de Claude
        """
        result = {
            'titulo_es': '',
            'texto_es': '',
            'resumen_corto': '',
            'resumen_medio': '',
            'resumen_largo': '',
            'hashtags': '',
            'categoria': 'General'
        }

        # Mapeo de etiquetas a claves del diccionario
        tags = {
            'TITULO_ES': 'titulo_es',
            'TEXTO_ES': 'texto_es',
            'RESUMEN_CORTO': 'resumen_corto',
            'RESUMEN_MEDIO': 'resumen_medio',
            'RESUMEN_LARGO': 'resumen_largo',
            'HASHTAGS': 'hashtags',
            'CATEGORIA': 'categoria'
        }

        for tag, key in tags.items():
            start_tag = f'[{tag}]'
            end_tag = f'[/{tag}]'

            start_idx = content.find(start_tag)
            end_idx = content.find(end_tag)

            if start_idx != -1 and end_idx != -1:
                value = content[start_idx + len(start_tag):end_idx].strip()
                result[key] = value

        return result

    def categorize_content(self, titulo: str, texto: str) -> str:
        """
        Categoriza el contenido si solo necesitas la categoría (más rápido)
        """
        prompt = f"""Categoriza el siguiente artículo en UNA de estas categorías:
Tutorial, Research, Tools, Case Study, News, Opinion, General

Título: {titulo}
Contenido: {texto[:500]}

Responde SOLO con el nombre de la categoría:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=50,
                temperature=0,
                messages=[{"role": "user", "content": prompt}]
            )

            categoria = response.content[0].text.strip()
            return categoria if categoria in ['Tutorial', 'Research', 'Tools', 'Case Study', 'News', 'Opinion'] else 'General'

        except Exception as e:
            logger.error(f"Error categorizando: {e}")
            return 'General'

    def batch_translate(self, noticias: List[Dict]) -> List[Dict]:
        """
        Traduce un lote de noticias

        Args:
            noticias: Lista de diccionarios con keys: titulo, texto, url

        Returns:
            Lista de resultados de traducción
        """
        results = []

        for i, noticia in enumerate(noticias):
            logger.info(f"Traduciendo noticia {i+1}/{len(noticias)}: {noticia.get('titulo', '')[:50]}...")

            result = self.translate_and_optimize(
                titulo=noticia.get('titulo', ''),
                texto=noticia.get('texto', ''),
                url=noticia.get('url', '')
            )

            # Agregar ID si existe
            if 'id' in noticia:
                result['id'] = noticia['id']

            results.append(result)

        return results


def test_translation_service():
    """
    Función de prueba para verificar el servicio
    """
    service = TranslationService()

    # Ejemplo de noticia
    test_article = {
        'titulo': 'New GPT-4 Model Achieves State-of-the-Art Results in Code Generation',
        'texto': 'OpenAI has released an updated version of GPT-4 that shows remarkable improvements in code generation tasks. The model demonstrates better understanding of programming contexts and can generate more accurate and efficient code across multiple programming languages.',
        'url': 'https://example.com/test-article'
    }

    result = service.translate_and_optimize(
        titulo=test_article['titulo'],
        texto=test_article['texto'],
        url=test_article['url']
    )

    print("=== Resultado de Traducción ===")
    for key, value in result.items():
        print(f"\n{key.upper()}:")
        print(value)
        print("-" * 80)


if __name__ == '__main__':
    # Configurar logging para pruebas
    logging.basicConfig(level=logging.INFO)
    test_translation_service()
