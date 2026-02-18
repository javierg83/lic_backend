-- Corrige los valores NULL en la columna 'estado' de la tabla 'licitaciones'
-- asignándoles un valor por defecto 'PENDIENTE'.
-- Requerido para cumplir con la validación de Pydantic (string no nulo).

UPDATE public.licitaciones
SET estado = 'PENDIENTE'
WHERE estado IS NULL;
