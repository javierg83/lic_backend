-- ==============================================================================
-- AUTO-GENERADO: ESQUEMA ACTUAL EN SUPABASE
-- Generado por exportar_esquema.py para contrastar con 100_full_schema_v3_compatible.sql
-- ==============================================================================

-- TABLA: adjudicaciones_licitacion
CREATE TABLE public.adjudicaciones_licitacion (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    licitacion_id uuid REFERENCES public.licitaciones(id),
    usuario text,
    monto_total_adjudicado NUMERIC,
    sucursal_envio_oc text,
    fecha_adjudicacion date,
    comentario text,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX adjudicaciones_licitacion_id_interno_key ON public.adjudicaciones_licitacion USING btree (id_interno);


-- TABLA: ai_token_usage_logs
CREATE TABLE public.ai_token_usage_logs (
    id SERIAL NOT NULL PRIMARY KEY,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    action VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens integer DEFAULT 0 NOT NULL,
    output_tokens integer DEFAULT 0 NOT NULL,
    total_tokens integer,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_token_usage_licitacion ON public.ai_token_usage_logs USING btree (licitacion_id);
CREATE INDEX idx_ai_token_usage_action ON public.ai_token_usage_logs USING btree (action);


-- TABLA: archivos_cotizaciones
CREATE TABLE public.archivos_cotizaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    adjudicacion_id uuid REFERENCES public.adjudicaciones_licitacion(id),
    nombre_archivo text,
    url_archivo text,
    formato text,
    peso_archivo_kb NUMERIC,
    sucursal_destino text,
    usuario_subio text,
    fecha_subida TIMESTAMP,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX archivos_cotizaciones_id_interno_key ON public.archivos_cotizaciones USING btree (id_interno);


-- TABLA: archivos_ordenes_compra
CREATE TABLE public.archivos_ordenes_compra (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    adjudicacion_id uuid REFERENCES public.adjudicaciones_licitacion(id),
    nombre_archivo text,
    url_archivo text,
    formato text,
    peso_archivo_kb NUMERIC,
    sucursal_destino text,
    usuario_subio text,
    fecha_subida TIMESTAMP,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX archivos_ordenes_compra_id_interno_key ON public.archivos_ordenes_compra USING btree (id_interno);


-- TABLA: auditoria_eventos
CREATE TABLE public.auditoria_eventos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    entidad text NOT NULL,
    entidad_id uuid NOT NULL,
    tipo_evento text NOT NULL,
    evento text NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos_json jsonb NOT NULL,
    usuario text
);

CREATE UNIQUE INDEX auditoria_eventos_id_interno_key ON public.auditoria_eventos USING btree (id_interno);


-- TABLA: auditoria_extracciones_campos
CREATE TABLE public.auditoria_extracciones_campos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    semantic_run_id uuid REFERENCES public.semantic_runs(id),
    concepto text NOT NULL,
    campo_extraido text NOT NULL,
    valor_extraido text,
    razonamiento text,
    lista_fuentes jsonb,
    creado_en TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_auditoria_campos_lic_concepto ON public.auditoria_extracciones_campos USING btree (licitacion_id, concepto);
CREATE INDEX idx_auditoria_campos_run ON public.auditoria_extracciones_campos USING btree (semantic_run_id);


-- TABLA: candidatos_homologacion
CREATE TABLE public.candidatos_homologacion (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    homologacion_id uuid REFERENCES public.homologaciones_productos(id),
    nombre_producto text,
    descripcion text,
    score_similitud NUMERIC,
    razonamiento text,
    ranking integer,
    stock_disponible integer,
    ubicacion_stock text,
    producto_codigo text,
    producto_nombre text,
    producto_descripcion text,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX candidatos_homologacion_id_interno_key ON public.candidatos_homologacion USING btree (id_interno);


-- TABLA: finanzas_licitacion
CREATE TABLE public.finanzas_licitacion (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    licitacion_id uuid REFERENCES public.licitaciones(id),
    tipo_documento text,
    descripcion text,
    monto NUMERIC,
    moneda text,
    documento_origen text,
    fuente_financiamiento text,
    glosa text,
    archivo_origen_id uuid REFERENCES public.licitacion_archivos(id),
    presupuesto_referencial NUMERIC,
    forma_pago text,
    plazo_pago text,
    garantias jsonb,
    multas jsonb,
    otros text,
    resumen text,
    updated_at TIMESTAMP DEFAULT now(),
    obsoleto boolean DEFAULT false,
    observaciones text
);

CREATE UNIQUE INDEX finanzas_licitacion_id_interno_key ON public.finanzas_licitacion USING btree (id_interno);


-- TABLA: gestion_licitacion_documentos
CREATE TABLE public.gestion_licitacion_documentos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    gestion_id uuid NOT NULL REFERENCES public.gestion_licitaciones(id),
    tipo_documento text NOT NULL,
    nombre_archivo text NOT NULL,
    ruta_archivo text NOT NULL,
    fecha_subida TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    usuario text,
    observacion text
);



-- TABLA: gestion_licitaciones
CREATE TABLE public.gestion_licitaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    estado text NOT NULL,
    monto NUMERIC,
    observaciones text,
    fecha_resultado date,
    fecha_cierre date,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

CREATE UNIQUE INDEX unique_licitacion_gestion ON public.gestion_licitaciones USING btree (licitacion_id);


-- TABLA: homologaciones_productos
CREATE TABLE public.homologaciones_productos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    licitacion_id uuid REFERENCES public.licitaciones(id),
    item_id uuid REFERENCES public.items_licitacion(id),
    item_key text,
    razonamiento text,
    input_tokens integer,
    output_tokens integer,
    modelo_usado text,
    fecha_homologacion TIMESTAMPTZ DEFAULT now(),
    descripcion_detectada text,
    obsoleto boolean DEFAULT false,
    razonamiento_general text,
    candidato_seleccionado_id uuid REFERENCES public.candidatos_homologacion(id)
);

CREATE UNIQUE INDEX homologaciones_productos_id_interno_key ON public.homologaciones_productos USING btree (id_interno);


-- TABLA: item_licitacion_especificaciones
CREATE TABLE public.item_licitacion_especificaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    item_id uuid REFERENCES public.items_licitacion(id),
    semantic_run_id uuid REFERENCES public.semantic_runs(id),
    especificacion text,
    tipo text,
    created_at TIMESTAMPTZ DEFAULT now(),
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX item_licitacion_especificaciones_id_interno_key ON public.item_licitacion_especificaciones USING btree (id_interno);


-- TABLA: items_licitacion
CREATE TABLE public.items_licitacion (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    licitacion_id uuid REFERENCES public.licitaciones(id),
    descripcion text,
    cantidad NUMERIC,
    unidad text,
    sku text,
    semantic_run_id uuid REFERENCES public.semantic_runs(id),
    archivo_origen_id uuid REFERENCES public.licitacion_archivos(id),
    item_key text,
    nombre_item text,
    observaciones text,
    fuente_resumen text,
    incompleto boolean,
    incompleto_motivos jsonb,
    tiene_descripcion_tecnica boolean,
    created_at TIMESTAMPTZ DEFAULT now(),
    adjudicado boolean DEFAULT false,
    proveedor text,
    precio_unitario NUMERIC,
    comentario_adjudicacion text,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX items_licitacion_id_interno_key ON public.items_licitacion USING btree (id_interno);
CREATE INDEX idx_items_licitacion_lic ON public.items_licitacion USING btree (licitacion_id);
CREATE INDEX idx_items_licitacion_run ON public.items_licitacion USING btree (semantic_run_id);


-- TABLA: licitacion_ai_metadata
CREATE TABLE public.licitacion_ai_metadata (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    ai_provider VARCHAR(50) NOT NULL,
    embedding_model VARCHAR(100) NOT NULL,
    llm_model VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX licitacion_ai_metadata_licitacion_id_key ON public.licitacion_ai_metadata USING btree (licitacion_id);


-- TABLA: licitacion_archivos
CREATE TABLE public.licitacion_archivos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    nombre_archivo_org text NOT NULL,
    ruta_almacenamiento text,
    tipo_contenido text,
    peso_bytes bigint,
    hash_md5 text,
    clasificacion_archivo text,
    estado_procesamiento text DEFAULT 'PENDIENTE'::text,
    estado_embedding boolean DEFAULT false,
    id_job_procesamiento text,
    mensaje_error text,
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_procesado TIMESTAMP,
    obsoleto boolean DEFAULT false
);

CREATE UNIQUE INDEX licitacion_archivos_id_interno_key ON public.licitacion_archivos USING btree (id_interno);
CREATE INDEX idx_lic_archivos_licitacion ON public.licitacion_archivos USING btree (licitacion_id);


-- TABLA: licitacion_entregas
CREATE TABLE public.licitacion_entregas (
    licitacion_id uuid NOT NULL PRIMARY KEY REFERENCES public.licitaciones(id),
    direccion_entrega VARCHAR(255),
    comuna_entrega VARCHAR(150),
    plazo_entrega VARCHAR(255),
    fecha_entrega VARCHAR(100),
    contacto_entrega VARCHAR(255),
    horario_entrega VARCHAR(255),
    instrucciones_entrega text,
    creado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);



-- TABLA: licitaciones
CREATE TABLE public.licitaciones (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    id_interno SERIAL NOT NULL,
    codigo_licitacion text,
    titulo text,
    descripcion text,
    nombre text,
    entidad_solicitante text,
    forma_pago text,
    plazo_pago text,
    moneda text,
    estado text DEFAULT 'ACTIVA'::text,
    usuario text,
    fecha_carga TIMESTAMPTZ DEFAULT now(),
    fecha_publicacion date,
    fecha_cierre date,
    fecha_adjudicacion date,
    obsoleto boolean DEFAULT false,
    estado_publicacion VARCHAR(50),
    unidad_compra text,
    tipo_licitacion VARCHAR(50) DEFAULT 'LICITACION_PUBLICA'::character varying
);

CREATE UNIQUE INDEX licitaciones_id_interno_key ON public.licitaciones USING btree (id_interno);
CREATE INDEX idx_licitaciones_codigo ON public.licitaciones USING btree (codigo_licitacion);
CREATE INDEX idx_licitaciones_fecha_carga ON public.licitaciones USING btree (fecha_carga);
CREATE INDEX idx_licitaciones_tipo_licitacion ON public.licitaciones USING btree (tipo_licitacion);


-- TABLA: semantic_evidences
CREATE TABLE public.semantic_evidences (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    semantic_run_id uuid NOT NULL REFERENCES public.semantic_runs(id),
    redis_key text NOT NULL,
    documento_id uuid REFERENCES public.licitacion_archivos(id),
    pagina integer,
    score_similitud NUMERIC,
    texto_fragmento text NOT NULL,
    creado_en TIMESTAMPTZ DEFAULT now() NOT NULL
);



-- TABLA: semantic_results
CREATE TABLE public.semantic_results (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    semantic_run_id uuid NOT NULL REFERENCES public.semantic_runs(id),
    concepto text NOT NULL,
    resultado_json jsonb NOT NULL,
    confianza_global NUMERIC,
    creado_en TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE UNIQUE INDEX semantic_results_semantic_run_id_key ON public.semantic_results USING btree (semantic_run_id);


-- TABLA: semantic_runs
CREATE TABLE public.semantic_runs (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    licitacion_id uuid NOT NULL REFERENCES public.licitaciones(id),
    concepto text NOT NULL,
    is_current boolean DEFAULT true NOT NULL,
    estado text DEFAULT 'OK'::text NOT NULL,
    mensaje_error text,
    prompt_version text,
    extractor_version text,
    top_k integer,
    min_score NUMERIC,
    creado_en TIMESTAMPTZ DEFAULT now() NOT NULL
);

CREATE INDEX idx_semantic_runs_lic_concepto ON public.semantic_runs USING btree (licitacion_id, concepto);
CREATE UNIQUE INDEX uq_semantic_runs_one_current ON public.semantic_runs USING btree (licitacion_id, concepto) WHERE (is_current = true);


-- TABLA: tabla_contenidos
CREATE TABLE public.tabla_contenidos (
    id SERIAL NOT NULL PRIMARY KEY,
    documento_id uuid REFERENCES public.licitacion_archivos(id),
    titulo text,
    pagina_inicio integer,
    pagina_fin integer,
    id_padre integer,
    nivel integer
);

CREATE INDEX idx_tabla_contenidos_doc ON public.tabla_contenidos USING btree (documento_id);


-- TABLA: usuarios
CREATE TABLE public.usuarios (
    id SERIAL NOT NULL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_usuario VARCHAR(100) NOT NULL,
    rol VARCHAR(50) DEFAULT 'analista'::character varying NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX usuarios_username_key ON public.usuarios USING btree (username);



