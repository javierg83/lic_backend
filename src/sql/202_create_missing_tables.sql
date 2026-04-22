-- ==============================================================================
-- SCRIPT: 202_create_missing_tables.sql  (versión corregida)
-- 
-- Crea ÚNICAMENTE las tablas que NO existen en la BD actual.
-- Tablas auditadas como faltantes:
--   - gestion_licitaciones
--   - gestion_licitacion_documentos
--
-- Ejecutar completo en el SQL Editor de Supabase (proyecto gjpmtazjiirresbbjasb).
-- ==============================================================================

-- -------------------------------------------------------------------------
-- 1. GESTIÓN DE LICITACIONES
-- Registro del estado comercial/operacional por licitación.
-- Columna licitacion_id referencia licitaciones_descargadas.id (uuid)
-- -------------------------------------------------------------------------
CREATE TABLE public.gestion_licitaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    licitacion_id uuid NOT NULL,
    estado character varying(50) NOT NULL DEFAULT 'EN_ANALISIS',
    monto numeric(15, 2),
    observaciones text,
    fecha_resultado date,
    fecha_cierre date,
    created_at timestamptz DEFAULT timezone('utc'::text, now()),
    updated_at timestamptz DEFAULT timezone('utc'::text, now()),
    CONSTRAINT pk_gestion_licitaciones PRIMARY KEY (id),
    CONSTRAINT uq_gestion_licitacion UNIQUE (licitacion_id),
    CONSTRAINT fk_gestion_licitaciones_licitacion
        FOREIGN KEY (licitacion_id)
        REFERENCES public.licitaciones_descargadas(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_gestion_licitaciones_licitacion_id
    ON public.gestion_licitaciones(licitacion_id);

-- -------------------------------------------------------------------------
-- 2. DOCUMENTOS DE GESTIÓN
-- Archivos adjuntos vinculados a la gestión de una licitación.
-- gestion_id referencia gestion_licitaciones.id (uuid)
-- -------------------------------------------------------------------------
CREATE TABLE public.gestion_licitacion_documentos (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    gestion_id uuid NOT NULL,
    tipo_documento character varying(100),
    nombre_archivo character varying(255),
    ruta_archivo text,
    fecha_subida timestamptz DEFAULT timezone('utc'::text, now()),
    usuario character varying(100),
    observacion text,
    CONSTRAINT pk_gestion_licitacion_documentos PRIMARY KEY (id),
    CONSTRAINT fk_gestion_docs_gestion
        FOREIGN KEY (gestion_id)
        REFERENCES public.gestion_licitaciones(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_gestion_docs_gestion_id
    ON public.gestion_licitacion_documentos(gestion_id);

-- ==============================================================================
-- FIN DEL SCRIPT - Verificación
-- ==============================================================================
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('gestion_licitaciones', 'gestion_licitacion_documentos')
ORDER BY table_name;
