-- ==============================================================================
-- SCRIPT: 203_test_clientes_usuarios.sql
-- Crea 2 empresas de prueba con sus usuarios para validar el flujo multi-tenant.
-- Ejecutar en el SQL Editor de Supabase (proyecto gjpmtazjiirresbbjasb).
-- ==============================================================================

-- ── 1. Crear empresas clientes ───────────────────────────────────────────────
INSERT INTO public.clientes (id, nombre, rut, activo)
VALUES 
    ('a1000000-0000-0000-0000-000000000001', 'Dental Sur SpA', '76.111.111-1', true),
    ('a2000000-0000-0000-0000-000000000002', 'TechSoluciones Ltda', '76.222.222-2', true)
ON CONFLICT (id) DO NOTHING;

-- ── 2. Crear preferencias (keywords de derivación) ───────────────────────────
INSERT INTO public.cliente_preferencias (cliente_id, palabras_clave_json)
VALUES
    ('a1000000-0000-0000-0000-000000000001', '["dental", "odontologia", "implante", "ortodoncia", "resina", "esterilizacion"]'),
    ('a2000000-0000-0000-0000-000000000002', '["computador", "servidor", "tecnologia", "software", "red", "telecomunicaciones"]')
ON CONFLICT (cliente_id) DO UPDATE 
    SET palabras_clave_json = EXCLUDED.palabras_clave_json;

-- ── 3. Crear usuarios de cada cliente ────────────────────────────────────────
-- NOTA: password_hash almacena texto plano por ahora (sin bcrypt aún en el sistema)
-- Usuario admin ya existente, no se toca.

INSERT INTO public.usuarios (username, password_hash, nombre_usuario, rol, cliente_id)
VALUES 
    ('clientedental', 'dental2024', 'Administrador Dental Sur', 'cliente', 'a1000000-0000-0000-0000-000000000001'),
    ('clientetech', 'tech2024',   'Administrador TechSoluciones', 'cliente', 'a2000000-0000-0000-0000-000000000002')
ON CONFLICT (username) DO UPDATE
    SET cliente_id = EXCLUDED.cliente_id,
        rol = EXCLUDED.rol,
        nombre_usuario = EXCLUDED.nombre_usuario;

-- ── 4. Verificación ──────────────────────────────────────────────────────────
SELECT 
    u.username,
    u.nombre_usuario,
    u.rol,
    c.nombre AS empresa,
    c.rut
FROM public.usuarios u
LEFT JOIN public.clientes c ON c.id = u.cliente_id
ORDER BY u.rol DESC, u.username;
