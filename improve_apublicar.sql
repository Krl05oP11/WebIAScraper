-- Script para mejorar la tabla apublicar
-- Prevenir duplicados y añadir constraints

-- 1. Crear índice único en URL para prevenir duplicados
-- Primero eliminamos duplicados existentes (mantiene el más reciente)
DELETE FROM apublicar a
USING apublicar b
WHERE a.id < b.id
  AND a.url = b.url;

-- Ahora creamos el constraint único
CREATE UNIQUE INDEX IF NOT EXISTS idx_apublicar_url_unique
ON apublicar(url);

-- 2. Agregar comentario al índice
COMMENT ON INDEX idx_apublicar_url_unique IS 'Previene URLs duplicadas en la cola de publicación';

-- 3. Ver estadísticas
SELECT
    COUNT(*) as total_noticias,
    COUNT(*) FILTER (WHERE publicado = true) as publicadas,
    COUNT(*) FILTER (WHERE publicado = false) as pendientes,
    COUNT(*) FILTER (WHERE procesado = true) as procesadas
FROM apublicar;

\echo '✅ Mejoras aplicadas a tabla apublicar'
