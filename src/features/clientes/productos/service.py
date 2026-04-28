import csv
import io
import re
from fastapi import UploadFile, HTTPException
from typing import List
from src.core.database import Database
from .schemas import UploadProductosResponse

class ClienteProductosService:
    @staticmethod
    async def upload_catalog(cliente_id: str, file: UploadFile) -> UploadProductosResponse:
        try:
            content = await file.read()

            # Detección de formato HTML (Excel Legacy .xls)
            is_html = b'<html' in content[:1000].lower() or b'<table' in content[:2000].lower()
            if is_html:
                return await ClienteProductosService._parse_html_xls(cliente_id, content)
            try:
                decoded_content = content.decode('utf-8-sig')
            except UnicodeDecodeError:
                try:
                    decoded_content = content.decode('latin-1')
                except Exception:
                    raise HTTPException(status_code=400, detail="El archivo no pudo ser decodificado (UTF-8 o Latin-1)")

            # Normalizar saltos de línea para evitar errores del módulo csv
            normalized_content = decoded_content.replace('\r\n', '\n').replace('\r', '\n')
            
            try:
                f = io.StringIO(normalized_content)
                csv_reader = csv.DictReader(f, delimiter=';')
                # Forzar lectura de cabeceras para validar delimitador
                if csv_reader.fieldnames and len(csv_reader.fieldnames) == 1 and ';' not in csv_reader.fieldnames[0] and ',' in csv_reader.fieldnames[0]:
                    f = io.StringIO(normalized_content)
                    csv_reader = csv.DictReader(f, delimiter=',')
            except Exception as e:
                 raise HTTPException(status_code=400, detail=f"Error al procesar el formato CSV: {str(e)}")

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

            total_insertados = await ClienteProductosService._insert_products(valid_items)

            return UploadProductosResponse(
                total_procesados=total_procesados,
                total_insertados=total_insertados,
                errores=errores
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    @staticmethod
    async def _parse_html_xls(cliente_id: str, content: bytes) -> UploadProductosResponse:
        try:
            html = content.decode('latin-1')
        except:
            html = content.decode('utf-8', errors='ignore')
            
        rows = re.findall(r'<tr.*?>(.*?)</tr>', html, re.IGNORECASE | re.DOTALL)
        
        valid_items = []
        errores = []
        total_procesados = 0
        
        for row in rows:
            cells = re.findall(r'<td.*?>(.*?)</td>', row, re.IGNORECASE | re.DOTALL)
            if not cells:
                continue
            
            # Limpiar HTML y entidades
            cells = [re.sub(r'<.*?>', '', c).replace('&nbsp;', ' ').strip() for c in cells]
            
            # Omitir encabezados o filas vacías
            if len(cells) < 3 or any(h in cells[0] for h in ["Informe de", "Articulo -", "Unidades"]):
                continue
                
            total_procesados += 1
            
            art_desc = cells[0]
            if '-' in art_desc:
                parts = art_desc.split('-', 1)
                codigo = parts[0].strip()
                nombre = parts[1].strip()
            else:
                codigo = None
                nombre = art_desc
                
            if not nombre:
                continue
                
            precio_val = None
            if len(cells) > 2:
                # Costo Vigente está en la columna 2
                p_str = cells[2].replace('.', '').replace(',', '.')
                try:
                    precio_val = float(p_str)
                except:
                    pass
            
            valid_items.append((cliente_id, codigo, nombre, None, precio_val))
            
        if not valid_items:
            raise HTTPException(status_code=400, detail="No se encontraron productos válidos en el archivo HTML-XLS.")
            
        total_insertados = await ClienteProductosService._insert_products(valid_items)
        
        return UploadProductosResponse(
            total_procesados=total_procesados,
            total_insertados=total_insertados,
            errores=errores
        )

    @staticmethod
    async def _insert_products(items: List[tuple]) -> int:
        conn = Database.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    from psycopg2.extras import execute_values
                    insert_query = """
                        INSERT INTO cliente_productos (cliente_id, codigo, nombre_producto, descripcion, precio_referencial)
                        VALUES %s
                    """
                    execute_values(cur, insert_query, items)
                    return len(items)
        except Exception as e:
            print(f"[Catalogo Error] {e}")
            raise HTTPException(status_code=500, detail="Error al intentar escribir en la base de datos.")
        finally:
            conn.close()

    @staticmethod
    async def get_products_by_client(cliente_id: str) -> List[dict]:
        conn = Database.get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, codigo, nombre_producto, descripcion, precio_referencial 
                    FROM cliente_productos 
                    WHERE cliente_id = %s 
                    ORDER BY created_at DESC
                """, (cliente_id,))
                rows = cur.fetchall()
                
                productos = []
                for row in rows:
                    productos.append({
                        "id": str(row[0]),
                        "codigo": row[1],
                        "nombre_producto": row[2],
                        "descripcion": row[3],
                        "precio_referencial": float(row[4]) if row[4] is not None else None
                    })
                return productos
        finally:
            conn.close()
