import csv
import io
from fastapi import UploadFile, HTTPException
from typing import List
from src.core.database import Database
from .schemas import UploadProductosResponse

class ClienteProductosService:
    @staticmethod
    async def upload_csv(cliente_id: str, file: UploadFile) -> UploadProductosResponse:
        content = await file.read()
        try:
            decoded_content = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            try:
                decoded_content = content.decode('latin-1')
            except Exception:
                raise HTTPException(status_code=400, detail="El archivo no pudo ser decodificado (UTF-8 o Latin-1)")

        csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=';') # typical in Chile/LATAM Excel exports, fallback to ',' later if needed
        # Fallback to comma if semicolon doesn't seem right (e.g. headers don't split)
        if csv_reader.fieldnames and len(csv_reader.fieldnames) == 1 and ';' not in csv_reader.fieldnames[0] and ',' in csv_reader.fieldnames[0]:
            csv_reader = csv.DictReader(io.StringIO(decoded_content), delimiter=',')

        # Normalize headers
        if not csv_reader.fieldnames:
            raise HTTPException(status_code=400, detail="El CSV está vacío o no tiene cabeceras")
            
        headers = [h.strip().lower() for h in csv_reader.fieldnames]
        
        # Expected column mapping
        col_nombre = next((h for h in headers if 'nombre' in h or 'producto' in h.lower()), None)
        if not col_nombre:
            raise HTTPException(status_code=400, detail="El CSV debe contener una columna para el nombre del producto ('nombre' o 'producto')")
            
        col_codigo = next((h for h in headers if 'cod' in h or 'sku' in h), None)
        col_desc = next((h for h in headers if 'desc' in h), None)
        col_precio = next((h for h in headers if 'precio' in h or 'valor' in h), None)

        total_procesados = 0
        total_insertados = 0
        errores = []
        
        # Parse items
        valid_items = []
        for row_idx, row_dict in enumerate(csv_reader):
            total_procesados += 1
            # Dictionary uses original headers but we know how to map them from our normalized logic
            # Let's map original header names back from the index
            orig_nombre = csv_reader.fieldnames[headers.index(col_nombre)]
            nombre_val = row_dict.get(orig_nombre, '').strip()
            
            if not nombre_val:
                errores.append(f"Fila {row_idx+2}: Nombre de producto vacío, se omitió.")
                continue
                
            codigo_val = row_dict.get(csv_reader.fieldnames[headers.index(col_codigo)], '').strip() if col_codigo else None
            desc_val = row_dict.get(csv_reader.fieldnames[headers.index(col_desc)], '').strip() if col_desc else None
            
            precio_val = None
            if col_precio:
                p_str = row_dict.get(csv_reader.fieldnames[headers.index(col_precio)], '').strip()
                p_str = p_str.replace('$', '').replace('.', '').replace(',', '.') # Normalize standard LATAM numbers
                try:
                    if p_str:
                        precio_val = float(p_str)
                except ValueError:
                    errores.append(f"Fila {row_idx+2}: Precio '{p_str}' inválido, se guardará en nulo.")

            valid_items.append((cliente_id, codigo_val, nombre_val, desc_val, precio_val))

        if not valid_items:
            raise HTTPException(status_code=400, detail="No se encontraron productos válidos para insertar.")

        # Batch insert to DB
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    # Borrar catalogo antiguo (opcional, o hacer upsert). El repo dice "cargar catálogo", idealmente borra el actual o se hace append.
                    # Haremos append por ahora, pero como la fase 1 dice cargar flexible, dejamos esto como inserción directa.
                    from psycopg2.extras import execute_values
                    insert_query = """
                        INSERT INTO cliente_productos (cliente_id, codigo, nombre_producto, descripcion, precio_referencial)
                        VALUES %s
                    """
                    execute_values(cur, insert_query, valid_items)
                    total_insertados = len(valid_items)
        except Exception as e:
            print(f"[Catalogo Error] {e}")
            raise HTTPException(status_code=500, detail="Error al intentar escribir en la base de datos.")
        finally:
            conn.close()

        return UploadProductosResponse(
            total_procesados=total_procesados,
            total_insertados=total_insertados,
            errores=errores
        )
