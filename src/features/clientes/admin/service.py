from typing import List, Optional
import uuid
from src.core.database import Database
from .schemas import ClienteCreate, ClienteResponse, ClienteDetailResponse

class AdminClienteService:
    @staticmethod
    def get_all_clientes() -> List[ClienteResponse]:
        conn = Database.get_connection()
        clientes = []
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre, rut, activo, created_at FROM clientes ORDER BY created_at DESC")
                rows = cur.fetchall()
                for row in rows:
                    clientes.append(ClienteResponse(
                        id=row[0],
                        nombre=row[1],
                        rut=row[2],
                        activo=row[3],
                        created_at=row[4]
                    ))
        finally:
            conn.close()
        return clientes

    @staticmethod
    def create_cliente(data: ClienteCreate) -> ClienteResponse:
        conn = Database.get_connection()
        new_id = str(uuid.uuid4())
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO clientes (id, nombre, rut, activo) VALUES (%s, %s, %s, %s) RETURNING created_at",
                        (new_id, data.nombre, data.rut, data.activo)
                    )
                    created_at = cur.fetchone()[0]
                    
                    # Inicializar preferencias vacías para el nuevo cliente
                    cur.execute(
                        "INSERT INTO cliente_preferencias (cliente_id, palabras_clave_json) VALUES (%s, %s)",
                        (new_id, '[]')
                    )
                    
            return ClienteResponse(
                id=new_id,
                nombre=data.nombre,
                rut=data.rut,
                activo=data.activo,
                created_at=created_at
            )
        finally:
            conn.close()

    @staticmethod
    def get_cliente_detail(cliente_id: str) -> Optional[ClienteDetailResponse]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, nombre, rut, activo, created_at FROM clientes WHERE id = %s", (cliente_id,))
                row = cur.fetchone()
                if not row:
                    return None
                
                # Obtener palabras clave
                cur.execute("SELECT palabras_clave_json FROM cliente_preferencias WHERE cliente_id = %s", (cliente_id,))
                pref_row = cur.fetchone()
                
                palabras = []
                if pref_row and pref_row[0]:
                    val = pref_row[0]
                    if isinstance(val, str):
                        import json
                        palabras = json.loads(val)
                    else:
                        palabras = val # Ya viene como lista (común en JSONB/psycopg2)
                
                return ClienteDetailResponse(
                    id=row[0],
                    nombre=row[1],
                    rut=row[2],
                    activo=row[3],
                    created_at=row[4],
                    palabras_clave=palabras
                )
        finally:
            conn.close()
