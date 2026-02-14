-- Script para agregar id_interno autogenerado a la tabla licitaciones

-- 1. Agregar columna id_interno como BIGINT autogenerado
ALTER TABLE licitaciones 
ADD COLUMN id_interno BIGINT GENERATED ALWAYS AS IDENTITY;

-- 2. Crear índice único para búsquedas rápidas por este ID
CREATE UNIQUE INDEX idx_licitaciones_id_interno ON licitaciones(id_interno);

-- Comentario: Al ser GENERATED ALWAYS AS IDENTITY, PostgreSQL se encarga de poblarlo
-- automáticamente para nuevas filas. Para filas existentes, las poblará al ejecutar el ALTER TABLE.
