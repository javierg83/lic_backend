-- SCRIPT DE MANTENIMIENTO: ELIMINAR TODAS LAS TABLAS RELACIONADAS A LICITACIONES
-- PRECAUCIÓN: ESTO ELIMINARÁ TODOS LOS DATOS. USAR CON EXTREMO CUIDADO.

-- 1. Eliminar tablas "hoja" (dependientes) primero, o usar CASCADE.
-- Usaremos CASCADE para asegurar que las dependencias se eliminen limpia y ordenadamente.

-- Licitaciones de Productos / Items
DROP TABLE IF EXISTS metadatos_documento CASCADE;
DROP TABLE IF EXISTS semantic_evidences CASCADE;
DROP TABLE IF EXISTS semantic_results CASCADE;
DROP TABLE IF EXISTS item_licitacion_especificaciones CASCADE;
DROP TABLE IF EXISTS item_evidences CASCADE;
DROP TABLE IF EXISTS item_especificaciones CASCADE;
DROP TABLE IF EXISTS candidatos_homologacion CASCADE;
DROP TABLE IF EXISTS homologaciones_productos CASCADE;
DROP TABLE IF EXISTS items_licitados CASCADE;
DROP TABLE IF EXISTS items_licitacion CASCADE;

-- Licitaciones de Finanzas
DROP TABLE IF EXISTS finanzas_garantias CASCADE;
DROP TABLE IF EXISTS finanzas_multas CASCADE;
DROP TABLE IF EXISTS finanzas_licitacion CASCADE;

-- Archivos y Runs
DROP TABLE IF EXISTS semantic_runs CASCADE;
DROP TABLE IF EXISTS licitacion_archivos CASCADE;
DROP TABLE IF EXISTS documentos CASCADE;

-- Tabla Principal
DROP TABLE IF EXISTS licitaciones CASCADE;

-- Eliminación de tipos ENUM si existen (opcional, verifica si tu schema los usa)
-- DROP TYPE IF EXISTS some_enum_type CASCADE;

-- Fin del script
