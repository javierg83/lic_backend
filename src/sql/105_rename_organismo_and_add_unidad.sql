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
