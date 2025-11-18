FROM python:3.11-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Descargar datos de NLTK (para extracción de temas)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copiar código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# Crear directorio para logs
RUN mkdir -p /app/logs

# Script de entrada
CMD ["python", "src/app.py"]
