-- ==============================================================================
-- MODELO DE BASE DE DATOS PARA GESTIÓN DE LICITACIONES - VERSIÓN COMPATIBLE (V3)
-- ==============================================================================
-- Este archivo es una versión extendida del modelo V2.
-- INCLUYE todos los campos y tablas requeridos por el código actual en producción:
-- - `lic_backend/src/features/licitaciones/actions/new/service.py`
-- - `lic_etl-semantic-extractor/src/services/licitacion_service.py`
-- - `lic_etl-document-extractor/src/nodes/search_table_contents.py`
--
-- CAMBIOS CLAVE RESPECTO A V2:
-- 1. Agrega alias de columnas para compatibilidad (ej: nombre vs titulo).
-- 2. Restaura tablas eliminadas en V2 pero usadas en código (tabla_contenidos).
-- 3. Agrega campos de metadatos faltantes en items y finanzas.
-- ==============================================================================

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ==========================================
-- 1. TABLA: licitaciones
-- ==========================================
CREATE TABLE IF NOT EXISTS public.licitaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    
    -- Campos V2
    codigo_licitacion TEXT,
    titulo TEXT,
    descripcion TEXT,
    organismo TEXT,
    
    -- Campos COMPATIBILIDAD CODIGO (service.py y licitacion_service.py)
    nombre TEXT, -- Usado en lugar de titulo por el backend
    organismo_solicitante TEXT, -- Usado en lugar de organismo por el extractor
    
    unidad_solicitante TEXT,
    forma_pago TEXT,
    plazo_pago TEXT,
    moneda TEXT,
    estado TEXT DEFAULT 'ACTIVA',
    usuario TEXT,
    
    fecha_carga TIMESTAMPTZ DEFAULT now(), -- Requerido por licitacion_service.py (ORDER BY)
    fecha_publicacion DATE,
    fecha_cierre DATE,
    fecha_adjudicacion DATE,
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_licitaciones_codigo ON public.licitaciones (codigo_licitacion);
CREATE INDEX IF NOT EXISTS idx_licitaciones_fecha_carga ON public.licitaciones (fecha_carga);


-- ==========================================
-- 2. TABLA: licitacion_archivos
-- Compatibilidad: service.py usa estos campos exactos.
-- ==========================================
CREATE TABLE IF NOT EXISTS public.licitacion_archivos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    licitacion_id UUID NOT NULL REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    nombre_archivo_org TEXT NOT NULL,
    ruta_almacenamiento TEXT,
    tipo_contenido TEXT,
    peso_bytes BIGINT,
    hash_md5 TEXT,
    clasificacion_archivo TEXT,
    estado_procesamiento TEXT DEFAULT 'PENDIENTE',
    estado_embedding BOOLEAN DEFAULT FALSE,
    id_job_procesamiento TEXT,
    mensaje_error TEXT,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesado TIMESTAMP,
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_lic_archivos_licitacion ON public.licitacion_archivos(licitacion_id);


-- ==========================================
-- 3. TABLA: tabla_contenidos
-- REQUERIDA POR: lic_etl-document-extractor/src/nodes/search_table_contents.py
-- Faltaba en V2.
-- ==========================================
CREATE TABLE IF NOT EXISTS public.tabla_contenidos (
    id SERIAL PRIMARY KEY,
    documento_id UUID REFERENCES public.licitacion_archivos(id) ON DELETE CASCADE,
    titulo TEXT,
    pagina_inicio INT,
    pagina_fin INT,
    id_padre INT, -- Autoreferencia para jerarquía
    nivel INT
);

CREATE INDEX IF NOT EXISTS idx_tabla_contenidos_doc ON public.tabla_contenidos(documento_id);


-- ==========================================
-- 4. TABLA: semantic_runs
-- REQUERIDA POR: lic_etl-semantic-extractor/src/services/semantic_extraction/runner.py
-- ==========================================
CREATE TABLE IF NOT EXISTS public.semantic_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    licitacion_id UUID NOT NULL REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    concepto TEXT NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    estado TEXT NOT NULL DEFAULT 'OK',
    mensaje_error TEXT,
    prompt_version TEXT,
    extractor_version TEXT,
    top_k INT,
    min_score NUMERIC(10,6),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_semantic_runs_lic_concepto ON public.semantic_runs (licitacion_id, concepto);
CREATE UNIQUE INDEX IF NOT EXISTS uq_semantic_runs_one_current ON public.semantic_runs (licitacion_id, concepto) WHERE is_current = true;


-- ==========================================
-- 5. TABLA: semantic_results
-- REQUERIDA POR: lic_etl-semantic-extractor/src/services/semantic_extraction/runner.py
-- ==========================================
CREATE TABLE IF NOT EXISTS public.semantic_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semantic_run_id UUID NOT NULL UNIQUE REFERENCES public.semantic_runs(id) ON DELETE CASCADE,
    concepto TEXT NOT NULL,
    resultado_json JSONB NOT NULL,
    confianza_global NUMERIC(10,6),
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ==========================================
-- 6. TABLA: semantic_evidences
-- REQUERIDA POR: lic_etl-semantic-extractor/src/services/semantic_extraction/runner.py
-- ==========================================
CREATE TABLE IF NOT EXISTS public.semantic_evidences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    semantic_run_id UUID NOT NULL REFERENCES public.semantic_runs(id) ON DELETE CASCADE,
    redis_key TEXT NOT NULL,
    documento_id UUID REFERENCES public.licitacion_archivos(id) ON DELETE SET NULL,
    pagina INT,
    score_similitud NUMERIC(10,6),
    texto_fragmento TEXT NOT NULL,
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);


-- ==========================================
-- 7. TABLA: items_licitacion
-- Consolidada V2 + Campos del Extractor
-- ==========================================
CREATE TABLE IF NOT EXISTS public.items_licitacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    licitacion_id UUID REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    
    -- Campos V2
    descripcion TEXT,
    cantidad NUMERIC,
    unidad TEXT,
    sku TEXT,
    
    -- Campos COMPATIBILIDAD CODIGO (licitacion_service.py)
    semantic_run_id UUID REFERENCES public.semantic_runs(id) ON DELETE SET NULL,
    archivo_origen_id UUID REFERENCES public.licitacion_archivos(id) ON DELETE SET NULL,
    item_key TEXT,
    nombre_item TEXT, -- Distinto de descripcion en el extractor
    observaciones TEXT,
    fuente_resumen TEXT,
    incompleto BOOLEAN,
    incompleto_motivos JSONB, -- O TEXT, extractor lo maneja como lista pero service lo formatea si es necesario, asumimos JSONB mejor
    tiene_descripcion_tecnica BOOLEAN,
    created_at TIMESTAMPTZ DEFAULT now(),

    -- Adjudicación (V2)
    adjudicado BOOLEAN DEFAULT FALSE,
    proveedor TEXT,
    precio_unitario NUMERIC,
    comentario_adjudicacion TEXT,
    
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_items_licitacion_lic ON public.items_licitacion(licitacion_id);
CREATE INDEX IF NOT EXISTS idx_items_licitacion_run ON public.items_licitacion(semantic_run_id);


-- ==========================================
-- 8. TABLA: item_licitacion_especificaciones
-- REQUERIDA POR: lic_etl-semantic-extractor/src/services/licitacion_service.py
-- Nota: V2 la llamaba `especificaciones_tecnicas`, pero el código usa este nombre.
-- ==========================================
CREATE TABLE IF NOT EXISTS public.item_licitacion_especificaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    item_id UUID REFERENCES public.items_licitacion(id) ON DELETE CASCADE,
    semantic_run_id UUID REFERENCES public.semantic_runs(id),
    
    especificacion TEXT, -- Usado por código en lugar de descripcion
    tipo TEXT, -- 'OBLIGATORIA', etc.
    created_at TIMESTAMPTZ DEFAULT now(),
    
    obsoleto BOOLEAN DEFAULT FALSE
);


-- ==========================================
-- 9. TABLA: finanzas_licitacion
-- Consolidada V2 + Campos Extensor Finanzas
-- ==========================================
CREATE TABLE IF NOT EXISTS public.finanzas_licitacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    licitacion_id UUID REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    
    -- V2 Base
    tipo_documento TEXT,
    descripcion TEXT,
    monto NUMERIC,
    moneda TEXT,
    documento_origen TEXT,
    fuente_financiamiento TEXT,
    glosa TEXT,
    archivo_origen_id UUID REFERENCES public.licitacion_archivos(id),
    
    -- Campos COMPATIBILIDAD CODIGO (licitacion_service.py)
    -- El extractor intenta guardar estos aqui, aunque V2 sugiera moverlos a licitaciones.
    presupuesto_referencial NUMERIC,
    forma_pago TEXT,
    plazo_pago TEXT,
    garantias JSONB, -- Extractor maneja dict/list
    multas JSONB,    -- Extractor maneja dict/list
    otros TEXT,
    resumen TEXT,
    updated_at TIMESTAMP DEFAULT now(),
    
    obsoleto BOOLEAN DEFAULT FALSE
);


-- ==========================================
-- 10. TABLA: homologaciones_productos
-- ==========================================
CREATE TABLE IF NOT EXISTS public.homologaciones_productos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    licitacion_id UUID REFERENCES public.licitaciones(id) ON DELETE CASCADE, -- Agregado para integridad con items
    item_id UUID REFERENCES public.items_licitacion(id) ON DELETE CASCADE,
    item_key TEXT, -- Usado para join lógico en licitacion_service.py
    
    razonamiento TEXT,
    input_tokens INTEGER,
    output_tokens INTEGER,
    
    modelo_usado TEXT,
    fecha_homologacion TIMESTAMPTZ DEFAULT now(),
    descripcion_detectada TEXT, -- Usado en licitacion_service.py
    
    obsoleto BOOLEAN DEFAULT FALSE
);


-- ==========================================
-- 11. TABLA: candidatos_homologacion
-- ==========================================
CREATE TABLE IF NOT EXISTS public.candidatos_homologacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    homologacion_id UUID REFERENCES public.homologaciones_productos(id) ON DELETE CASCADE,
    
    nombre_producto TEXT,
    descripcion TEXT,
    score_similitud NUMERIC,
    razonamiento TEXT,
    ranking INTEGER,
    
    -- Campos usados en licitacion_service.py
    stock_disponible INT,
    ubicacion_stock TEXT,
    producto_codigo TEXT,
    producto_nombre TEXT, -- Alias si nombre_producto no basta
    producto_descripcion TEXT, -- Alias
    
    obsoleto BOOLEAN DEFAULT FALSE
);


-- ==========================================
-- 12. TABLAS ADICIONALES DE NEGOCIO (V2)
-- Adjudicaciones, Cotizaciones, OC, Auditoría
-- ==========================================

CREATE TABLE IF NOT EXISTS public.adjudicaciones_licitacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    licitacion_id UUID REFERENCES public.licitaciones(id),
    usuario TEXT,
    monto_total_adjudicado NUMERIC,
    sucursal_envio_oc TEXT,
    fecha_adjudicacion DATE,
    comentario TEXT,
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.archivos_cotizaciones (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    adjudicacion_id UUID REFERENCES public.adjudicaciones_licitacion(id),
    nombre_archivo TEXT,
    url_archivo TEXT,
    formato TEXT,
    peso_archivo_kb NUMERIC,
    sucursal_destino TEXT,
    usuario_subio TEXT,
    fecha_subida TIMESTAMP,
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.archivos_ordenes_compra (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    adjudicacion_id UUID REFERENCES public.adjudicaciones_licitacion(id),
    nombre_archivo TEXT,
    url_archivo TEXT,
    formato TEXT,
    peso_archivo_kb NUMERIC,
    sucursal_destino TEXT,
    usuario_subio TEXT,
    fecha_subida TIMESTAMP,
    obsoleto BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS public.auditoria_eventos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    id_interno SERIAL UNIQUE,
    entidad TEXT NOT NULL,
    entidad_id UUID NOT NULL,
    tipo_evento TEXT NOT NULL,
    evento TEXT NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_json JSONB NOT NULL,
    usuario TEXT
);
