-- Agregar columna para enlazar al candidato seleccionado definitivamente
ALTER TABLE public.homologaciones_productos 
ADD COLUMN IF NOT EXISTS candidato_seleccionado_id UUID REFERENCES public.candidatos_homologacion(id) ON DELETE SET NULL;
