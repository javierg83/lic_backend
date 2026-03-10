-- Add tipo_licitacion column to licitaciones table
ALTER TABLE licitaciones 
ADD COLUMN tipo_licitacion VARCHAR(50) DEFAULT 'LICITACION_PUBLICA';

-- Create an index to speed up filtering if needed in the future
CREATE INDEX idx_licitaciones_tipo_licitacion ON licitaciones(tipo_licitacion);
