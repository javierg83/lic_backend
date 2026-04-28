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
                cur.execute("""
                    SELECT c.id, c.nombre, c.rut, c.activo, c.created_at, 
                           COALESCE(cc.alerta_homologacion_umbral, 60.0)
                    FROM clientes c
                    LEFT JOIN cliente_configuracion cc ON c.id = cc.cliente_id
                    ORDER BY c.created_at DESC
                """)
                rows = cur.fetchall()
                for row in rows:
                    clientes.append(ClienteResponse(
                        id=row[0],
                        nombre=row[1],
                        rut=row[2],
                        activo=row[3],
                        created_at=row[4],
                        umbral=float(row[5])
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
                    
                    # Inicializar configuración de alertas
                    cur.execute(
                        "INSERT INTO cliente_configuracion (cliente_id) VALUES (%s)",
                        (new_id,)
                    )

                    # Crear usuario inicial si se provee, o uno por defecto
                    username = data.admin_username if data.admin_username else f"admin_{data.rut.replace('.', '').replace('-', '')}"
                    password = data.admin_password if data.admin_password else "inicio2024"
                    
                    cur.execute(
                        "INSERT INTO usuarios (username, password_hash, nombre_usuario, rol, cliente_id) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
                        (username, password, f"Admin {data.nombre}", 'cliente', new_id)
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
                
                # Obtener el primer usuario administrador asociado
                cur.execute("SELECT username FROM usuarios WHERE cliente_id = %s AND rol = 'cliente' LIMIT 1", (cliente_id,))
                user_row = cur.fetchone()
                admin_username = user_row[0] if user_row else None
                
                # Obtener configuración
                cur.execute("SELECT alerta_homologacion_umbral, alerta_homologacion_activa, correo_contacto FROM cliente_configuracion WHERE cliente_id = %s", (cliente_id,))
                conf_row = cur.fetchone()
                umbral = float(conf_row[0]) if conf_row and conf_row[0] is not None else 60.0
                activa = conf_row[1] if conf_row and conf_row[1] is not None else True
                correo = conf_row[2] if conf_row else None
                
                # Obtener total de productos
                cur.execute("SELECT COUNT(*) FROM cliente_productos WHERE cliente_id = %s", (cliente_id,))
                total_productos = cur.fetchone()[0]

                return ClienteDetailResponse(
                    id=row[0],
                    nombre=row[1],
                    rut=row[2],
                    activo=row[3],
                    created_at=row[4],
                    palabras_clave=palabras,
                    admin_username=admin_username,
                    umbral=umbral,
                    alerta_homologacion_activa=activa,
                    correo_contacto=correo,
                    total_productos=total_productos
                )
        finally:
            conn.close()

    @staticmethod
    def update_user_password(username: str, new_password: str) -> bool:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE usuarios SET password_hash = %s WHERE username = %s",
                        (new_password, username)
                    )
                    return cur.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def create_user_for_client(cliente_id: str, username: str, password: str, nombre: str) -> bool:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO usuarios (username, password_hash, nombre_usuario, rol, cliente_id) VALUES (%s, %s, %s, %s, %s)",
                        (username, password, nombre, 'cliente', cliente_id)
                    )
                    return True
        finally:
            conn.close()
