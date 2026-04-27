-- 1. Crear la nueva tabla de categorías por cliente
CREATE TABLE IF NOT EXISTS public.cliente_categorias (
    id uuid DEFAULT gen_random_uuid() NOT NULL PRIMARY KEY,
    cliente_id uuid NOT NULL REFERENCES public.clientes(id) ON DELETE CASCADE,
    codigo_categoria VARCHAR(50) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cliente_categoria UNIQUE (cliente_id, codigo_categoria)
);

-- 2. Añadir columna a items_licitacion
ALTER TABLE public.items_licitacion ADD COLUMN IF NOT EXISTS codigo_categoria VARCHAR(50);

-- 3. Añadir columna a cliente_productos (Catálogo de clientes para el motor híbrido)
ALTER TABLE public.cliente_productos ADD COLUMN IF NOT EXISTS codigo_categoria VARCHAR(50);
