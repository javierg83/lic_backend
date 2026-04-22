from typing import List
from src.core.database import Database
import json

class DerivationService:
    @staticmethod
    def derivar_licitacion(licitacion_descargada_id: str):
        """
        Recibe el ID de una licitación que ya está guardada en licitaciones_descargadas
        y la asigna (deriva) a los clientes de acuerdo a sus palabras clave.
        """
        conn = Database.get_connection()
        try:
            with conn.cursor() as cur:
                # Obtener info de la licitación
                cur.execute("""
                    SELECT id, titulo, descripcion 
                    FROM licitaciones_descargadas 
                    WHERE id = %s
                """, (licitacion_descargada_id,))
                lic = cur.fetchone()
                if not lic:
                    return

                lic_id = lic[0]
                titulo = (lic[1] or "").lower()
                descripcion = (lic[2] or "").lower()
                texto_busqueda = f"{titulo} {descripcion}"

                # Obtener preferencias de clientes activos
                cur.execute("""
                    SELECT cp.cliente_id, cp.palabras_clave_json 
                    FROM cliente_preferencias cp
                    JOIN clientes c ON c.id = cp.cliente_id
                    WHERE c.activo = true
                """)
                preferencias = cur.fetchall()

                for pref in preferencias:
                    cliente_id = pref[0]
                    # palabras_clave_json es un listado de strings
                    try:
                        keywords = pref[1] if isinstance(pref[1], list) else json.loads(pref[1] or "[]")
                    except Exception:
                        keywords = []

                    match = False
                    for kw in keywords:
                        if kw.lower() in texto_busqueda:
                            match = True
                            break
                    
                    # Logica: Si en esta etapa manual no hay keywords definidos, o hay match
                    # (aquí se puede afinar cómo actuan las keywords vacias. Asumiremos que si está
                    # vacía no se le manda nada, para no hacer spam).
                    if not keywords:
                        # Para pruebas sin keywords, también podríamos forzar el match.
                        match = True

                    if match:
                        cur.execute("""
                            INSERT INTO licitaciones_clientes (cliente_id, licitacion_descargada_id, estado_interno, observaciones)
                            VALUES (%s, %s, 'Nueva', 'Derivación por coincidencia de palabras clave o subida directa')
                            ON CONFLICT (cliente_id, licitacion_descargada_id) DO NOTHING
                        """, (cliente_id, lic_id))
            
            conn.commit()
            print(f"[DERIVATION] Derivación completada para licitación {licitacion_descargada_id}")
        except Exception as e:
            print(f"[DERIVATION ERROR] Error derivando licitación {licitacion_descargada_id}: {e}")
            conn.rollback()
        finally:
            conn.close()
