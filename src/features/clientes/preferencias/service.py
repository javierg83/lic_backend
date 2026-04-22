import json
from src.core.database import Database
from .schemas import ClientePreferenciasResponse, ClientePreferenciasUpdate

class ClientePreferenciasService:
    @staticmethod
    def get_preferencias(cliente_id: str) -> ClientePreferenciasResponse:
        query = "SELECT palabras_clave_json FROM cliente_preferencias WHERE cliente_id = %s"
        row = Database.execute_query(query, (cliente_id,), fetch_all=False)
        
        if not row:
            return ClientePreferenciasResponse(cliente_id=cliente_id, palabras_clave=[])
        
        keywords = row["palabras_clave_json"]
        if isinstance(keywords, str):
            keywords = json.loads(keywords)
            
        return ClientePreferenciasResponse(cliente_id=cliente_id, palabras_clave=keywords)

    @staticmethod
    def update_preferencias(cliente_id: str, data: ClientePreferenciasUpdate) -> ClientePreferenciasResponse:
        keywords_json = json.dumps(data.palabras_clave)
        
        # Delete then insert to avoid needing a UNIQUE constraint
        delete_query = "DELETE FROM cliente_preferencias WHERE cliente_id = %s"
        Database.execute_non_query(delete_query, (cliente_id,))

        insert_query = """
            INSERT INTO cliente_preferencias (cliente_id, palabras_clave_json)
            VALUES (%s, %s)
        """
        Database.execute_non_query(insert_query, (cliente_id, keywords_json))
        
        return ClientePreferenciasResponse(cliente_id=cliente_id, palabras_clave=data.palabras_clave)
