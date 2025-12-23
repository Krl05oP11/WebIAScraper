-- Migration: Increase resumen_medio field from 500 to 1000 characters
-- Date: 2025-12-23
-- Description: Increase character limit for Facebook summaries to accommodate longer content
-- Author: WebIAScrap Team

-- Increase column size (non-blocking operation in PostgreSQL)
ALTER TABLE apublicar
ALTER COLUMN resumen_medio TYPE VARCHAR(1000);

-- Add comment to document the change
COMMENT ON COLUMN apublicar.resumen_medio IS 'Resumen medio para Facebook - máximo 1000 caracteres';

-- Verify the change
-- Expected output: resumen_medio | character varying(1000)
-- Run after migration: \d apublicar
