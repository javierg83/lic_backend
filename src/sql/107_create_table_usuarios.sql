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
