-- Migration: Fix temas column type - convert VARCHAR to text[] array
-- Date: 2025-12-24
-- Description: Convert temas column from VARCHAR (string) to text[] (array) to fix JSON serialization
-- Author: WebIAScrap Team

-- Step 1: Convert existing data from PostgreSQL array string format to proper array
-- Examples: '{Tutorial/News,Towards-Ai,Llm}' becomes ['Tutorial/News','Towards-Ai','Llm']

-- For noticias table
ALTER TABLE noticias
ALTER COLUMN temas TYPE text[] USING (
    CASE
        -- If it's a string with PostgreSQL array format {item1,item2,item3}
        WHEN temas IS NOT NULL AND temas::text LIKE '{%}' THEN
            string_to_array(
                trim(both '{}' from temas::text),
                ','
            )
        -- If it's a regular comma-separated string
        WHEN temas IS NOT NULL AND temas::text LIKE '%,%' THEN
            string_to_array(temas::text, ',')
        -- If it's a single value
        WHEN temas IS NOT NULL AND temas::text != '' THEN
            ARRAY[temas::text]
        -- If it's NULL or empty
        ELSE
            NULL
    END
);

-- For apublicar table
ALTER TABLE apublicar
ALTER COLUMN temas TYPE text[] USING (
    CASE
        -- If it's a string with PostgreSQL array format {item1,item2,item3}
        WHEN temas IS NOT NULL AND temas::text LIKE '{%}' THEN
            string_to_array(
                trim(both '{}' from temas::text),
                ','
            )
        -- If it's a regular comma-separated string
        WHEN temas IS NOT NULL AND temas::text LIKE '%,%' THEN
            string_to_array(temas::text, ',')
        -- If it's a single value
        WHEN temas IS NOT NULL AND temas::text != '' THEN
            ARRAY[temas::text]
        -- If it's NULL or empty
        ELSE
            NULL
    END
);

-- Add comments to document the change
COMMENT ON COLUMN noticias.temas IS 'Lista de temas - PostgreSQL text[] array';
COMMENT ON COLUMN apublicar.temas IS 'Lista de temas - PostgreSQL text[] array';

-- Verification queries (run manually after migration):
-- SELECT id, titulo, temas, pg_typeof(temas) as tipo_temas FROM noticias LIMIT 5;
-- SELECT id, titulo, temas, pg_typeof(temas) as tipo_temas FROM apublicar LIMIT 5;
