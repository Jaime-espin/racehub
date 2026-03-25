-- Agregar columnas faltantes a la tabla resultados
ALTER TABLE IF EXISTS resultados 
ADD COLUMN IF NOT EXISTS posicion_categoria INTEGER;

ALTER TABLE IF EXISTS resultados 
ADD COLUMN IF NOT EXISTS confianza INTEGER;

-- Verificar
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'resultados'
ORDER BY ordinal_position;
