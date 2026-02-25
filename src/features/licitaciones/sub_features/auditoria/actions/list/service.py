from src.core.database import Database
from uuid import UUID

def get_auditoria(licitacion_id: UUID) -> list[dict]:
    query = """
        SELECT 
            id, 
            licitacion_id, 
            semantic_run_id, 
            concepto, 
            campo_extraido, 
            valor_extraido, 
            razonamiento, 
            lista_fuentes, 
            creado_en
        FROM auditoria_extracciones_campos
        WHERE licitacion_id = %(lic_id)s
        ORDER BY concepto, campo_extraido, creado_en DESC
    """
    
    # execute_query uses RealDictCursor and returns a list of dictionaries if fetch_all=True
    result = Database.execute_query(query, {"lic_id": str(licitacion_id)})
    
    auditoria = []
    if result:
        for row in result:
            auditoria.append({
                "id": row["id"],
                "licitacion_id": row["licitacion_id"],
                "semantic_run_id": row["semantic_run_id"],
                "concepto": row["concepto"],
                "campo_extraido": row["campo_extraido"],
                "valor_extraido": row["valor_extraido"],
                "razonamiento": row["razonamiento"],
                "lista_fuentes": row["lista_fuentes"],
                "creado_en": row["creado_en"]
            })
            
    return auditoria

