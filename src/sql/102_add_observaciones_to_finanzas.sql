-- Agrega la columna 'observaciones' a la tabla 'finanzas_licitacion'
-- Requerido por DatosEconomicosShowService (lic_backend)

ALTER TABLE public.finanzas_licitacion
ADD COLUMN IF NOT EXISTS observaciones TEXT;
