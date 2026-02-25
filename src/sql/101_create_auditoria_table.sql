-- ==========================================
-- SCRIPT DE CREACIÓN PARA TABLA DE AUDITORÍA DE EXTRACCIÓN SEMÁNTICA
-- Ejecutar en la base de datos PostgreSQL principal
-- ==========================================

-- Esta tabla almacenará el razonamiento del modelo y las fuentes documentales 
-- específicas (documento, página, párrafo) utilizadas para extraer cada campo clave.

CREATE TABLE IF NOT EXISTS public.auditoria_extracciones_campos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    licitacion_id UUID NOT NULL REFERENCES public.licitaciones(id) ON DELETE CASCADE,
    semantic_run_id UUID REFERENCES public.semantic_runs(id) ON DELETE CASCADE,
    
    -- El concepto o categoría de la extracción (ej: 'DATOS_BASICOS', 'ITEMS_LICITACION', 'FINANZAS')
    concepto TEXT NOT NULL,
    
    -- El campo específico al que aplica (ej: 'presupuesto_referencial', 'nombre_item', 'forma_pago')
    campo_extraido TEXT NOT NULL,
    
    -- Valor extraído convertido a texto para visualización de referencia
    valor_extraido TEXT,
    
    -- Explicación en lenguaje natural del porqué el LLM asignó este valor
    razonamiento TEXT,
    
    -- Array de objetos JSON indicando las fuentes exactas utilizadas.
    -- Formato esperado: [{"documento": "bases.pdf", "pagina": 5, "parrafos": ["texto 1", "texto 2"]}]
    lista_fuentes JSONB,
    
    creado_en TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Índices recomendados para poder buscar auditorías rápidamente por licitación y concepto
CREATE INDEX IF NOT EXISTS idx_auditoria_campos_lic_concepto ON public.auditoria_extracciones_campos (licitacion_id, concepto);
CREATE INDEX IF NOT EXISTS idx_auditoria_campos_run ON public.auditoria_extracciones_campos (semantic_run_id);
