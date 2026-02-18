-- Add estado_publicacion column to licitaciones table
ALTER TABLE licitaciones
ADD COLUMN IF NOT EXISTS estado_publicacion VARCHAR(50);

-- Comment on column
COMMENT ON COLUMN licitaciones.estado_publicacion IS 'Estado de negocio de la licitación extraído de los documentos (ej. Publicada, Cerrada, Desierta). Diferente del estado del sistema.';
