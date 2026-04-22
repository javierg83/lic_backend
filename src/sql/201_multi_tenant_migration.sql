-- ==============================================================================
-- MIGRACIÓN: Arquitectura Multi-Tenant (Soporte Multi-Cliente)
-- Fase 1: Creación de estructuras core e independización de la homologación
-- ==============================================================================

-- 1. Renombrar tabla principal (la Verdad Global)
ALTER TABLE public.licitaciones RENAME TO licitaciones_descargadas;

-- Renombrar los índices principales para evitar confusión
ALTER INDEX IF EXISTS licitaciones_id_interno_key RENAME TO licitaciones_descargadas_id_interno_key;
ALTER INDEX IF EXISTS idx_licitaciones_codigo RENAME TO idx_licitaciones_descargadas_codigo;
ALTER INDEX IF EXISTS idx_licitaciones_fecha_carga RENAME TO idx_licitaciones_descargadas_fecha_carga;
ALTER INDEX IF EXISTS idx_licitaciones_tipo_licitacion RENAME TO idx_licitaciones_descargadas_tipo_licitacion;

-- 2. Crear Tabla Clientes (Catálogo de empresas que usan el sistema)
CREATE TABLE public.clientes (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rut VARCHAR(20),
    activo boolean DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 3. Crear Tabla Cliente Preferencias (Filtros de derivación)
CREATE TABLE public.cliente_preferencias (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    cliente_id uuid NOT NULL REFERENCES public.clientes(id) ON DELETE CASCADE,
    palabras_clave_json jsonb DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- 4. Crear Tabla Cliente Productos (El catálogo propio de cada cliente)
CREATE TABLE public.cliente_productos (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    cliente_id uuid NOT NULL REFERENCES public.clientes(id) ON DELETE CASCADE,
    codigo VARCHAR(100),
    nombre_producto text NOT NULL,
    descripcion text,
    precio_referencial NUMERIC,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_cliente_productos_cliente_id ON public.cliente_productos(cliente_id);

-- 5. Crear Tabla Licitaciones Clientes (El Buzón / Bandeja del cliente)
CREATE TABLE public.licitaciones_clientes (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    cliente_id uuid NOT NULL REFERENCES public.clientes(id) ON DELETE CASCADE,
    licitacion_descargada_id uuid NOT NULL REFERENCES public.licitaciones_descargadas(id) ON DELETE CASCADE,
    estado_interno VARCHAR(50) DEFAULT 'Nueva',
    fecha_derivacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    observaciones text,
    CONSTRAINT uq_licitacion_cliente UNIQUE (cliente_id, licitacion_descargada_id)
);
CREATE INDEX idx_licitaciones_clientes_cliente_id ON public.licitaciones_clientes(cliente_id);
CREATE INDEX idx_licitaciones_clientes_lic_desc_id ON public.licitaciones_clientes(licitacion_descargada_id);

-- 6. Vincular Usuarios a su respectivo cliente
ALTER TABLE public.usuarios ADD COLUMN cliente_id uuid REFERENCES public.clientes(id) ON DELETE SET NULL;

-- 7. Actualizar la Homologación
-- Vincular candidatos al catálogo del cliente
ALTER TABLE public.candidatos_homologacion ADD COLUMN cliente_producto_id uuid REFERENCES public.cliente_productos(id) ON DELETE SET NULL;

-- Vincular las homologaciones a la copia privada de la licitación del cliente
ALTER TABLE public.homologaciones_productos ADD COLUMN licitacion_cliente_id uuid REFERENCES public.licitaciones_clientes(id) ON DELETE CASCADE;

-- 8. Actualizar Gestión 
ALTER TABLE IF EXISTS public.adjudicaciones_licitacion ADD COLUMN licitacion_cliente_id uuid REFERENCES public.licitaciones_clientes(id) ON DELETE CASCADE;
ALTER TABLE IF EXISTS public.gestion_licitaciones ADD COLUMN licitacion_cliente_id uuid REFERENCES public.licitaciones_clientes(id) ON DELETE CASCADE;


-- ==============================================================================
-- POST-MIGRACIÓN: Creación del Cliente "Global" Legacy (Dummie de contingencia)
-- Para que los registros actuales de `pre_licitaciones` no queden huérfanos.
-- ==============================================================================
DO $$
DECLARE
    legacy_cliente_id uuid;
BEGIN
    -- Crear el cliente legacy
    INSERT INTO public.clientes (nombre, rut, activo) 
    VALUES ('Cliente Global Inicial', '11111111-1', true) 
    RETURNING id INTO legacy_cliente_id;
    
    -- Asociar a los usuarios pre-existentes a este cliente
    UPDATE public.usuarios SET cliente_id = legacy_cliente_id;

    -- Replicar todas las licitaciones globales que existan hacia este buzón
    INSERT INTO public.licitaciones_clientes (cliente_id, licitacion_descargada_id, estado_interno, observaciones)
    SELECT legacy_cliente_id, id, 'Migrada', 'Añadida durante migración estructural'
    FROM public.licitaciones_descargadas
    ON CONFLICT (cliente_id, licitacion_descargada_id) DO NOTHING;

    -- Update de las foreing keys de gestion_licitaciones usando EXECUTE para evitar error de parseo si tabla no existe
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'gestion_licitaciones') THEN
        EXECUTE 'UPDATE public.gestion_licitaciones gl
                 SET licitacion_cliente_id = lc.id
                 FROM public.licitaciones_clientes lc
                 WHERE lc.licitacion_descargada_id = gl.licitacion_id 
                   AND lc.cliente_id = $1' USING legacy_cliente_id;
    END IF;

    -- Update de las foreing keys de homologaciones_productos
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'homologaciones_productos') THEN
        EXECUTE 'UPDATE public.homologaciones_productos hp
                 SET licitacion_cliente_id = lc.id
                 FROM public.licitaciones_clientes lc
                 WHERE lc.licitacion_descargada_id = hp.licitacion_id 
                   AND lc.cliente_id = $1' USING legacy_cliente_id;
    END IF;

    -- Update de las foreing keys de adjudicaciones_licitacion
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'adjudicaciones_licitacion') THEN
        EXECUTE 'UPDATE public.adjudicaciones_licitacion al
                 SET licitacion_cliente_id = lc.id
                 FROM public.licitaciones_clientes lc
                 WHERE lc.licitacion_descargada_id = al.licitacion_id 
                   AND lc.cliente_id = $1' USING legacy_cliente_id;
    END IF;

END $$;
