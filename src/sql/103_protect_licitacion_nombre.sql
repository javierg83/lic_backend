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
