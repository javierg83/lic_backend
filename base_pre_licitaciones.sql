-- ====================================
-- SCRIPT: src/sql/100_full_schema_v3_compatible.sql
-- ====================================
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


-- ====================================
-- SCRIPT: src/sql/101_add_candidato_seleccionado.sql
-- ====================================
-- Agregar columna para enlazar al candidato seleccionado definitivamente
ALTER TABLE public.homologaciones_productos 
ADD COLUMN IF NOT EXISTS candidato_seleccionado_id UUID REFERENCES public.candidatos_homologacion(id) ON DELETE SET NULL;


-- ====================================
-- SCRIPT: src/sql/101_create_auditoria_table.sql
-- ====================================
-- ==========================================
-- SCRIPT DE CREACIÓN PARA TABLA DE AUDITORÍA DE EXTRACCIÓN SEMÁNTICA
-- Ejecutar en la base de datos PostgreSQL principal
-- ==========================================

-- Esta tabla almacenará el razonamiento del modelo y las fuentes documentales 
-- específicas (documento, página, párrafo) utilizadas para extraer cada campo clave.

CREATE TABLE IF NOT EXISTS public.auditoria_extracciones_campos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    licitacion_id UUID NOT NULL REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    semantic_run_id UUID REFERENCES public.semantic_runs(id) ON DELETE CASCADE,
    
    -- El concepto o categoría de la extracción (ej: 'DATOS_BASICOS', 'ITEMS_LICITACION', 'FINANZAS')
    concepto TEXT NOT NULL,
    
    -- El campo específico al que aplica (ej: 'presupuesto_referencial', 'nombre_item', 'forma_pago')
    campo_extraido TEXT NOT NULL,
    
    -- Valor extraído convertido a texto para visualización de referencia
    valor_extraido TEXT,
    
    -- Explicación en lenguaje natural del porqué el LLM asignó este valor
    razonamiento TEXT,
    
    -- Array de objetos JSON indicando las fuentes exactas utilizadas.
    -- Formato esperado: [{"documento": "bases.pdf", "pagina": 5, "parrafos": ["texto 1", "texto 2"]}]
    lista_fuentes JSONB,
    
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices recomendados para poder buscar auditorías rápidamente por licitación y concepto
CREATE INDEX IF NOT EXISTS idx_auditoria_campos_lic_concepto ON public.auditoria_extracciones_campos (licitacion_id, concepto);
CREATE INDEX IF NOT EXISTS idx_auditoria_campos_run ON public.auditoria_extracciones_campos (semantic_run_id);


-- ====================================
-- SCRIPT: src/sql/101_fix_null_estados.sql
-- ====================================
-- Corrige los valores NULL en la columna 'estado' de la tabla 'licitaciones'
-- asignándoles un valor por defecto 'PENDIENTE'.
-- Requerido para cumplir con la validación de Pydantic (string no nulo).

UPDATE public.licitaciones
SET estado = 'PENDIENTE'
WHERE estado IS NULL;


-- ====================================
-- SCRIPT: src/sql/102_add_observaciones_to_finanzas.sql
-- ====================================
-- Agrega la columna 'observaciones' a la tabla 'finanzas_licitacion'
-- Requerido por DatosEconomicosShowService (lic_backend)

ALTER TABLE public.finanzas_licitacion
ADD COLUMN IF NOT EXISTS observaciones TEXT;


-- ====================================
-- SCRIPT: src/sql/103_protect_licitacion_nombre.sql
-- ====================================
-- ==============================================================================
-- PRESERVACIÓN DE NOMBRE ORIGINAL (REDIRECCIÓN)
-- ==============================================================================
-- El requerimiento es mantener el 'nombre' ingresado en el formulario.
-- Como el extractor intenta sobrescribir 'nombre' con el título del documento,
-- este trigger intercepta ese cambio y lo REDIRIGE a la columna 'titulo'.
--
-- De esta forma:
-- 1. 'nombre' se mantiene intacto (valor del formulario).
-- 2. El valor que traía el extractor se guarda en 'titulo' (dato extra).

CREATE OR REPLACE FUNCTION redirect_licitacion_name_update()
RETURNS TRIGGER AS $$
BEGIN
    -- Si se intenta cambiar el nombre...
    IF NEW.nombre IS DISTINCT FROM OLD.nombre THEN
        -- Redirigimos el nuevo valor a la columna 'titulo'
        NEW.titulo := NEW.nombre;
        
        -- Y forzamos que 'nombre' mantenga su valor original
        NEW.nombre := OLD.nombre;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Limpieza preventiva
DROP TRIGGER IF EXISTS trg_redirect_licitacion_name ON public.licitaciones;

-- Instalación del Trigger
CREATE TRIGGER trg_redirect_licitacion_name
BEFORE UPDATE ON public.licitaciones
FOR EACH ROW
EXECUTE FUNCTION redirect_licitacion_name_update();


-- ====================================
-- SCRIPT: src/sql/104_add_estado_publicacion.sql
-- ====================================
-- Add estado_publicacion column to licitaciones table
ALTER TABLE licitaciones
ADD COLUMN IF NOT EXISTS estado_publicacion VARCHAR(50);

-- Comment on column
COMMENT ON COLUMN licitaciones.estado_publicacion IS 'Estado de negocio de la licitación extraído de los documentos (ej. Publicada, Cerrada, Desierta). Diferente del estado del sistema.';


-- ====================================
-- SCRIPT: src/sql/105_rename_organismo_and_add_unidad.sql
-- ====================================
-- ==============================================================================
-- MIGRACIÓN SEGURA: RENOMBRAR COLUMNAS PARA EXTRACTOR DE ENTIDAD V2
-- ==============================================================================
-- Script idempotente (se puede ejecutar varias veces sin romper)

DO $$
BEGIN

    -- 1. Manejo de 'ORGANISMO_SOLICITANTE' -> 'ENTIDAD_SOLICITANTE'
    -- -------------------------------------------------------------
    -- Si existe 'organismo_solicitante' y NO existe 'entidad_solicitante', renombramos.
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='organismo_solicitante') 
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='entidad_solicitante') THEN
        
        ALTER TABLE public.licitaciones RENAME COLUMN organismo_solicitante TO entidad_solicitante;
        RAISE NOTICE '✅ Columna organismo_solicitante renombrada a entidad_solicitante';
        
    ELSIF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='organismo_solicitante') 
          AND EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='entidad_solicitante') THEN
        
        -- Ambas existen (pudo fallar una migración previa a medias). Migramos datos de la vieja a la nueva.
        UPDATE public.licitaciones 
        SET entidad_solicitante = organismo_solicitante 
        WHERE entidad_solicitante IS NULL;
        
        -- Opcional: Borrar la vieja si ya migramos. (Comentar si se prefiere mantener por seguridad)
        -- ALTER TABLE public.licitaciones DROP COLUMN organismo_solicitante;
        RAISE NOTICE '⚠️ Ambas columnas (organismo y entidad) existían. Se migraron datos a entidad_solicitante.';
        
    ELSE
        RAISE NOTICE 'ℹ️ La columna entidad_solicitante ya existe (o no existía organismo). No se requiere acción.';
    END IF;


    -- 2. Asegurar existencia de 'UNIDAD_COMPRA'
    -- -----------------------------------------
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='unidad_compra') THEN
        ALTER TABLE public.licitaciones ADD COLUMN unidad_compra TEXT;
        RAISE NOTICE '✅ Columna unidad_compra creada.';
    END IF;


    -- 3. Manejo de 'UNIDAD_SOLICITANTE' (Deprecada) -> 'UNIDAD_COMPRA'
    -- ----------------------------------------------------------------
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='unidad_solicitante') THEN
        
        -- Migrar datos si unidad_compra está vacía
        UPDATE public.licitaciones 
        SET unidad_compra = unidad_solicitante 
        WHERE unidad_compra IS NULL;
        
        RAISE NOTICE '🔄 Datos de unidad_solicitante migrados a unidad_compra.';
        
        -- Renombrar o Borrar la vieja para evitar confusión. 
        -- Al renombrar, si el target existe, falla (el error que tuviste).
        -- Mejor BORRAR la vieja ya que ya migramos los datos arriba.
        ALTER TABLE public.licitaciones DROP COLUMN unidad_solicitante;
        RAISE NOTICE '🗑️ Columna antigua unidad_solicitante eliminada tras migración.';
        
    END IF;

END $$;


-- ====================================
-- SCRIPT: src/sql/106_add_tipo_licitacion.sql
-- ====================================
-- Add tipo_licitacion column to licitaciones table
ALTER TABLE licitaciones 
ADD COLUMN tipo_licitacion VARCHAR(50) DEFAULT 'LICITACION_PUBLICA';

-- Create an index to speed up filtering if needed in the future
CREATE INDEX idx_licitaciones_tipo_licitacion ON licitaciones(tipo_licitacion);


-- ====================================
-- SCRIPT: src/sql/107_create_table_usuarios.sql
-- ====================================
-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Por ahora guardaremos texto plano o hash simple según se implemente en el backend
    nombre_usuario VARCHAR(100) NOT NULL,
    rol VARCHAR(50) NOT NULL DEFAULT 'analista',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insertar usuario administrador
INSERT INTO usuarios (username, password_hash, nombre_usuario, rol)
VALUES ('admin', 'licitacion26', 'Administrador del Sistema', 'admin');

-- Insertar usuario analista (estándar)
INSERT INTO usuarios (username, password_hash, nombre_usuario, rol)
VALUES ('analista', 'licitacion26', 'Analista de Licitaciones', 'analista');


-- ====================================
-- SCRIPT: src/sql/108_create_licitacion_ai_metadata.sql
-- ====================================
-- TABLA DE METADATOS DE IA POR LICITACION
-- Se separa de la tabla principal 'licitaciones' para mantener la modularización y flexibilidad.
-- Permite saber con qué "marca" y "modelo" se indexó cada licitación.

CREATE TABLE IF NOT EXISTS licitacion_ai_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    licitacion_id UUID NOT NULL REFERENCES licitaciones(id) ON DELETE CASCADE,
    ai_provider VARCHAR(50) NOT NULL,            -- 'openai', 'google'
    embedding_model VARCHAR(100) NOT NULL,        -- 'text-embedding-3-small', 'models/text-embedding-004'
    llm_model VARCHAR(100) NOT NULL,              -- 'gpt-4o', 'gemini-2.5-pro'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(licitacion_id)
);

COMMENT ON TABLE licitacion_ai_metadata IS 'Almacena la marca y modelos de IA utilizados para procesar cada licitación, asegurando consistencia entre embeddings y extracción.';


-- ====================================
-- SCRIPT: src/sql/create_ai_token_usage_logs.sql
-- ====================================
CREATE TABLE IF NOT EXISTS ai_token_usage_logs (
    id SERIAL PRIMARY KEY,
    licitacion_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_licitacion
        FOREIGN KEY(licitacion_id) 
        REFERENCES licitaciones(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_ai_token_usage_licitacion ON ai_token_usage_logs(licitacion_id);
CREATE INDEX idx_ai_token_usage_action ON ai_token_usage_logs(action);


-- ====================================
-- SCRIPT: src/sql/999_cleanup_organismo_columns.sql
-- ====================================
-- ==============================================================================
-- LIMPIEZA FINAL: ELIMINAR COLUMNAS OBSOLETAS
-- ==============================================================================
-- Este script elimina las columnas 'organismo' y 'organismo_solicitante' si existen.
-- Úsalo con precaución una vez asegurado que el código usa 'entidad_solicitante'.

DO $$
BEGIN

    -- 1. Eliminar columna 'organismo' (si existe)
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='organismo') THEN
        ALTER TABLE public.licitaciones DROP COLUMN organismo;
        RAISE NOTICE '🗑️ Columna "organismo" eliminada.';
    ELSE
        RAISE NOTICE 'ℹ️ Columna "organismo" no existe.';
    END IF;

    -- 2. Eliminar columna 'organismo_solicitante' (si existe y ya migramos a 'entidad_solicitante')
    -- Nota: El script de migración anterior (105) intentaba renombrarla. 
    -- Si por alguna razón sigue existiendo (por ej, si no se ejecutó el rename sino un copy), la borramos.
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='organismo_solicitante') THEN
         -- Verificar que exista la nueva antes de borrar la vieja
        IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='licitaciones' AND column_name='entidad_solicitante') THEN
            ALTER TABLE public.licitaciones DROP COLUMN organismo_solicitante;
            RAISE NOTICE '🗑️ Columna "organismo_solicitante" eliminada (ya existe entidad_solicitante).';
        ELSE
            RAISE WARNING '⚠️ NO SE BORRÓ "organismo_solicitante" porque no se detectó "entidad_solicitante". Ejecuta primero la migración.';
        END IF;
    END IF;

END $$;


