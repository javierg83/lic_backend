-- Corrige los valores NULL en la columna 'estado' de la tabla 'licitaciones'
-- asignándoles un valor por defecto 'PENDIENTE' (o el que corresponda según lógica de negocio).
-- Esto es necesario para cumplir con la validación de Pydantic que exige un string no nulo.

UPDATE public.licitaciones
SET estado = 'PENDIENTE'
WHERE estado IS NULL;

-- Opcional: Asegurar que no vuelvan a insertarse nulos en el futuro
-- ALTER TABLE public.licitaciones ALTER COLUMN estado SET DEFAULT 'PENDIENTE';
-- ALTER TABLE public.licitaciones ALTER COLUMN estado SET NOT NULL;
