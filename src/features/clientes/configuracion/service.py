from typing import Optional
from src.core.database import Database
from .schemas import ClienteConfiguracionResponse, ClienteConfiguracionUpdate

class ClienteConfiguracionService:
    @staticmethod
    def get_configuracion(cliente_id: str) -> ClienteConfiguracionResponse:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT alerta_homologacion_umbral, alerta_homologacion_activa, correo_contacto FROM cliente_configuracion WHERE cliente_id = %s",
                    (cliente_id,)
                )
                row = cur.fetchone()
                
                if not row:
                    # Si no existe, crear la configuración por defecto
                    cur.execute(
                        "INSERT INTO cliente_configuracion (cliente_id) VALUES (%s) RETURNING alerta_homologacion_umbral, alerta_homologacion_activa, correo_contacto",
                        (cliente_id,)
                    )
                    row = cur.fetchone()
                    conn.commit()
                
                return ClienteConfiguracionResponse(
                    cliente_id=cliente_id,
                    alerta_homologacion_umbral=float(row[0]) if row[0] is not None else 60.0,
                    alerta_homologacion_activa=row[1] if row[1] is not None else True,
                    correo_contacto=row[2]
                )
        finally:
            conn.close()

    @staticmethod
    def update_configuracion(cliente_id: str, data: ClienteConfiguracionUpdate) -> ClienteConfiguracionResponse:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Asegurar que el registro exista
                    cur.execute(
                        "INSERT INTO cliente_configuracion (cliente_id) VALUES (%s) ON CONFLICT (cliente_id) DO NOTHING",
                        (cliente_id,)
                    )
                    
                    cur.execute(
                        """
                        UPDATE cliente_configuracion 
                        SET 
                            alerta_homologacion_umbral = COALESCE(%s, alerta_homologacion_umbral),
                            alerta_homologacion_activa = COALESCE(%s, alerta_homologacion_activa),
                            correo_contacto = COALESCE(%s, correo_contacto),
                            updated_at = CURRENT_TIMESTAMP
                        WHERE cliente_id = %s
                        RETURNING alerta_homologacion_umbral, alerta_homologacion_activa, correo_contacto
                        """,
                        (data.alerta_homologacion_umbral, data.alerta_homologacion_activa, data.correo_contacto, cliente_id)
                    )
                    row = cur.fetchone()
                    
                    return ClienteConfiguracionResponse(
                        cliente_id=cliente_id,
                        alerta_homologacion_umbral=float(row[0]) if row[0] is not None else 60.0,
                        alerta_homologacion_activa=row[1] if row[1] is not None else True,
                        correo_contacto=row[2]
                    )
        finally:
            conn.close()
