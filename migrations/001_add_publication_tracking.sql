-- Migration: Add publication tracking columns to apublicar table
-- Date: 2025-11-18
-- Description: Add columns for tracking social media publications

-- Add new columns for publication tracking
ALTER TABLE apublicar
ADD COLUMN IF NOT EXISTS publicado BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS plataformas_publicadas JSONB,
ADD COLUMN IF NOT EXISTS intentos_publicacion INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS ultimo_error TEXT,
ADD COLUMN IF NOT EXISTS published_at TIMESTAMP;

-- Create index on publicado column for faster queries
CREATE INDEX IF NOT EXISTS idx_apublicar_publicado ON apublicar(publicado);

-- Create index on procesado column for faster queries
CREATE INDEX IF NOT EXISTS idx_apublicar_procesado ON apublicar(procesado);

-- Update existing rows
UPDATE apublicar
SET publicado = FALSE,
    intentos_publicacion = 0
WHERE publicado IS NULL;

-- Add comment to table
COMMENT ON COLUMN apublicar.publicado IS 'Indica si la noticia ha sido publicada en al menos una plataforma';
COMMENT ON COLUMN apublicar.plataformas_publicadas IS 'JSON con información de publicaciones por plataforma';
COMMENT ON COLUMN apublicar.intentos_publicacion IS 'Número de intentos de publicación realizados';
COMMENT ON COLUMN apublicar.ultimo_error IS 'Último error de publicación si hubo';
COMMENT ON COLUMN apublicar.published_at IS 'Timestamp de la primera publicación exitosa';
