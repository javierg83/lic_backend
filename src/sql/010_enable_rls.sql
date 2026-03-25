-- Activar Row Level Security (RLS) en todas las tablas del esquema public
-- Esto resuelve la alerta de seguridad "Table publicly accessible" de Supabase
-- 
-- IMPORTANTE:
-- Al activar RLS sin agregar políticas, el acceso a las tablas mediante
-- la API de PostgREST con la clave anon (pública) quedará bloqueado por completo.
-- Dado que el frontend se conecta al backend (FastAPI) y el backend se conecta a
-- la base de datos usando SQLAlchemy con la URL de conexión (rol "postgres", que tiene
-- bypassrls), la aplicación seguirá funcionando sin problemas, pero el endpoint de
-- datos de Supabase quedará seguro frente a ataques externos no autorizados.

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'ALTER TABLE public.' || quote_ident(r.tablename) || ' ENABLE ROW LEVEL SECURITY;';
    END LOOP;
END;
$$;
