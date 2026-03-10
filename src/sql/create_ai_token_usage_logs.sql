CREATE TABLE IF NOT EXISTS ai_token_usage_logs (
    id SERIAL PRIMARY KEY,
    licitacion_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(100) NOT NULL,
    input_tokens INTEGER NOT NULL DEFAULT 0,
    output_tokens INTEGER NOT NULL DEFAULT 0,
    total_tokens INTEGER GENERATED ALWAYS AS (input_tokens + output_tokens) STORED,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_licitacion
        FOREIGN KEY(licitacion_id) 
        REFERENCES licitaciones(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_ai_token_usage_licitacion ON ai_token_usage_logs(licitacion_id);
CREATE INDEX idx_ai_token_usage_action ON ai_token_usage_logs(action);
