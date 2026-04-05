-- TABLA DE METADATOS DE IA POR LICITACION
-- Se separa de la tabla principal 'licitaciones' para mantener la modularización y flexibilidad.
-- Permite saber con qué "marca" y "modelo" se indexó cada licitación.

CREATE TABLE IF NOT EXISTS licitacion_ai_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    licitacion_id UUID NOT NULL REFERENCES licitaciones(id) ON DELETE CASCADE,
    ai_provider VARCHAR(50) NOT NULL,            -- 'openai', 'google'
    embedding_model VARCHAR(100) NOT NULL,        -- 'text-embedding-3-small', 'models/text-embedding-004'
    llm_model VARCHAR(100) NOT NULL,              -- 'gpt-4o', 'gemini-2.5-pro'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(licitacion_id)
);

COMMENT ON TABLE licitacion_ai_metadata IS 'Almacena la marca y modelos de IA utilizados para procesar cada licitación, asegurando consistencia entre embeddings y extracción.';
