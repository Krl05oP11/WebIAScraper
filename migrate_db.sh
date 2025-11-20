#!/bin/bash

# Script de migración de base de datos para WebIAScraper
# Añade columnas de tracking de publicaciones en redes sociales

echo "================================================"
echo "📊 Migración de Base de Datos - WebIAScraper"
echo "================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar que docker-compose está corriendo
if ! docker-compose ps | grep -q "webiascrap_db.*Up"; then
    echo -e "${RED}❌ Error: La base de datos no está corriendo${NC}"
    echo "Por favor, inicia los servicios con: docker-compose up -d"
    exit 1
fi

echo -e "${YELLOW}⚠️  Esta migración añadirá las siguientes columnas a la tabla 'apublicar':${NC}"
echo "  - publicado (BOOLEAN)"
echo "  - plataformas_publicadas (JSONB)"
echo "  - intentos_publicacion (INTEGER)"
echo "  - ultimo_error (TEXT)"
echo "  - published_at (TIMESTAMP)"
echo ""
echo "También creará índices para mejorar el rendimiento."
echo ""

read -p "¿Deseas continuar? (s/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    echo "Migración cancelada."
    exit 0
fi

echo ""
echo "🔄 Ejecutando migración..."
echo ""

# Ejecutar migración
docker-compose exec -T db psql -U webiauser -d webiascrap << 'EOF'
-- Migration: Add publication tracking columns to apublicar table
-- Date: 2025-11-18

\echo '📝 Añadiendo columnas...'

-- Add new columns for publication tracking
ALTER TABLE apublicar
ADD COLUMN IF NOT EXISTS publicado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS plataformas_publicadas JSONB,
ADD COLUMN IF NOT EXISTS intentos_publicacion INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS ultimo_error TEXT,
ADD COLUMN IF NOT EXISTS published_at TIMESTAMP;

\echo '✅ Columnas añadidas'
\echo ''
\echo '📇 Creando índices...'

-- Create index on publicado column for faster queries
CREATE INDEX IF NOT EXISTS idx_apublicar_publicado ON apublicar(publicado);

-- Create index on procesado column for faster queries
CREATE INDEX IF NOT EXISTS idx_apublicar_procesado ON apublicar(procesado);

\echo '✅ Índices creados'
\echo ''
\echo '🔄 Actualizando registros existentes...'

-- Update existing rows
UPDATE apublicar
SET publicado = FALSE,
    intentos_publicacion = 0
WHERE publicado IS NULL;

\echo '✅ Registros actualizados'
\echo ''
\echo '📝 Añadiendo comentarios...'

-- Add comments to table
COMMENT ON COLUMN apublicar.publicado IS 'Indica si la noticia ha sido publicada en al menos una plataforma';
COMMENT ON COLUMN apublicar.plataformas_publicadas IS 'JSON con información de publicaciones por plataforma';
COMMENT ON COLUMN apublicar.intentos_publicacion IS 'Número de intentos de publicación realizados';
COMMENT ON COLUMN apublicar.ultimo_error IS 'Último error de publicación si hubo';
COMMENT ON COLUMN apublicar.published_at IS 'Timestamp de la primera publicación exitosa';

\echo '✅ Comentarios añadidos'
\echo ''
\echo '📊 Verificando estructura de la tabla...'

-- Verify structure
\d apublicar

EOF

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}================================================${NC}"
    echo -e "${GREEN}✅ Migración completada exitosamente${NC}"
    echo -e "${GREEN}================================================${NC}"
    echo ""
    echo "La tabla 'apublicar' ahora tiene las columnas necesarias para"
    echo "el tracking de publicaciones en redes sociales."
    echo ""
    echo "Puedes continuar con la configuración de SocialPublisher."
else
    echo ""
    echo -e "${RED}================================================${NC}"
    echo -e "${RED}❌ Error durante la migración${NC}"
    echo -e "${RED}================================================${NC}"
    echo ""
    echo "Por favor, revisa los mensajes de error arriba."
    echo "Si necesitas ayuda, contacta al administrador."
    exit 1
fi
