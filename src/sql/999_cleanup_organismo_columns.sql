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
