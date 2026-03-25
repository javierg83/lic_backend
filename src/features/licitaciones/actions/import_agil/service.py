import httpx
import re
import os
import io
import json
from fastapi import UploadFile
from typing import List, Optional
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from src.core.responses import ApiResponse
from src.core.config import COMPRA_AGIL_BEARER, COMPRA_AGIL_USER_KEY, COMPRA_AGIL_API_KEY
from .schemas import ImportCompraAgilResponse, ArchivoCompraAgilResponse
from src.features.licitaciones.actions.new.service import LicitacionNewService

class CompraAgilService:
    BASE_URL_SEARCH = "https://api.buscador.mercadopublico.cl"
    BASE_URL_ADJUNTO = "https://adjunto.mercadopublico.cl"

    @staticmethod
    def _extract_code(url_or_code: str) -> str:
        # Regex to find patterns like: 1738-77-COT26
        match = re.search(r'\b\d+-\d+-[A-Za-z0-9]+\b', url_or_code)
        if match:
            return match.group(0)
        return url_or_code.strip()

    UNIDADES_MAP = {
        "EA": "Unidades",
        "UN": "Unidades",
        "UND": "Unidades",
        "BX": "Cajas",
        "CJ": "Cajas",
        "PAQ": "Paquetes",
        "BG": "Bolsas",
        "VI": "Frascos",
        "AMP": "Ampollas",
        "CMP": "Comprimidos",
        "SET": "Set",
        "KIT": "Kit",
        "PACK": "Pack",
        "GR": "Gramos",
        "KG": "Kilogramos",
        "ML": "Mililitros",
        "LT": "Litros",
        "M": "Metros",
        "M2": "Metros Cuadrados",
        "M3": "Metros Cúbicos",
        "000": "Millar / Adhesivo"
    }

    @staticmethod
    def _capture_web_screenshot(codigo: str) -> bytes:
        """
        Captura la ficha de Mercado Público como una imagen generándola en memoria RAM.
        Utiliza Selenium para asegurar fidelidad visual.
        """
        import base64
        import time
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from PIL import Image

        url = f"https://buscador.mercadopublico.cl/ficha?code={codigo}"
        print(f"[TRACE] Capturando pantalla completa para: {url}")

        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1280,1080')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(url)
            time.sleep(8) # Espera a carga inicial
            
            # Scroll para asegurar carga de datos (lazy loading)
            total_height = driver.execute_script("return document.body.scrollHeight")
            driver.set_window_size(1280, total_height)
            time.sleep(2)

            # Capturar usando CDP para resolución completa
            result = driver.execute_cdp_cmd("Page.captureScreenshot", {
                "format": "png",
                "captureBeyondViewport": True
            })
            
            # Convertir a PDF usando Pillow
            img = Image.open(io.BytesIO(base64.b64decode(result['data'])))
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            pdf_buffer = io.BytesIO()
            img.save(pdf_buffer, "PDF", resolution=100.0)
            pdf_bytes = pdf_buffer.getvalue()
            print(f"[TRACE] PDF fotográfico generado en memoria")
            
            return pdf_bytes

        except Exception as e:
            print(f"[ERROR] Fallo en captura de pantalla Selenium: {e}")
            raise e
        finally:
            driver.quit()

    @staticmethod
    async def import_compra_agil(url_or_code: str) -> ApiResponse[ImportCompraAgilResponse]:
        print(f"==== INICIANDO PROCESO DE IMPORTACIÓN COMPRA ÁGIL ====")
        print(f"[TRACE] Entrada recibida: {url_or_code}")
        
        codigo = CompraAgilService._extract_code(url_or_code)
        print(f"[TRACE] Código extraído validado: {codigo}")
        
        if not codigo:
            print("[ERROR] No se pudo extraer un código válido de Compra Ágil.")
            return ApiResponse.fail(message="No se pudo extraer un código válido de Compra Ágil de la entrada.")

        print("[TRACE] Preparando importación en memoria (sin descargas físicas)")

        timeout_config = httpx.Timeout(45.0, connect=45.0)
        async with httpx.AsyncClient(timeout=timeout_config) as client:
            print("[TRACE] Evaluando extracción de información base...")
            # 1. Check Historical/Details if needed. Here we just fetch the Attachments.
            # You can add logic to fetch "Ficha" and save it as a PDF or JSON to the UploadFile list 
            # if you want the IA to extract from the Ficha itself too.
            # Let's fetch the list of attachments.
            print("[TRACE] (Nota: Ahora extrayendo 'ficha/información base' directo de la API además de los adjuntos).")
            
            # --- NUEVO: Extraer Ficha de Datos Básicos ---
            ficha_url = f"{CompraAgilService.BASE_URL_SEARCH}/compra-agil?action=ficha&code={codigo}"
            print(f"[TRACE] Solicitando ficha de datos a URL: {ficha_url}")
            
            # API del buscador exige x-api-key y Authorization
            headers_buscador = {
                "Authorization": f"Bearer {COMPRA_AGIL_BEARER}",
                "x-api-key": COMPRA_AGIL_API_KEY or "",
                "Content-Type": "application/json",
                "Origin": "https://www.mercadopublico.cl",
                "Referer": "https://www.mercadopublico.cl/"
            }
            
            res_ficha = await client.get(ficha_url, headers=headers_buscador)
            print(f"[TRACE] Respuesta ficha recibida. Status Code: {res_ficha.status_code}")
            
            archivos_procesados = []
            upload_files = []

            if res_ficha.status_code == 200:
                try:
                    ficha_json = res_ficha.json()
                    ficha_nombre_json = f"ficha_datos_{codigo}.json"
                    ficha_nombre_pdf = f"ficha_datos_{codigo}.pdf"
                    
                    # 1. Mantener JSON Original en memoria
                    archivos_procesados.append(ArchivoCompraAgilResponse(nombre=ficha_nombre_json, ruta="MEMORIA", uuid="ficha_json"))
                    
                    # 2. CAPTURAR WEB SCREENSHOT (Para ETL y Visualización)
                    print(f"[TRACE] Capturando pantalla de la ficha web oficial...")
                    pdf_bytes = CompraAgilService._capture_web_screenshot(codigo)
                    
                    archivos_procesados.append(ArchivoCompraAgilResponse(nombre=ficha_nombre_pdf, ruta="MEMORIA", uuid="ficha_pdf"))
                    
                    # Preparar el PDF para envío al procesamiento
                    file_like_pdf = io.BytesIO(pdf_bytes)
                    upload_files.append(UploadFile(file=file_like_pdf, filename=ficha_nombre_pdf))
                    print(f"[TRACE] Ficha PDF (Captura Web) generada e integrada para procesamiento.")
                    
                    # Preparar el JSON para envío al procesamiento (NUEVO: Para inyección de ítems)
                    file_like_json = io.BytesIO(res_ficha.content)
                    upload_files.append(UploadFile(file=file_like_json, filename=ficha_nombre_json))
                    print(f"[TRACE] Ficha JSON integrada para procesamiento estructurado.")
                    
                except Exception as e:
                    print(f"[ERROR] Error al procesar datos de la ficha JSON/PDF: {e}")
            else:
                print(f"[WARNING] No se pudo obtener la ficha de datos. Status: {res_ficha.status_code}")

            
            # API de djuntos exige user_key y Authorization
            headers_adjunto = {
                "Authorization": f"Bearer {COMPRA_AGIL_BEARER}",
                "user_key": COMPRA_AGIL_USER_KEY or "",
                "Content-Type": "application/json",
                "Origin": "https://www.mercadopublico.cl",
                "Referer": "https://www.mercadopublico.cl/"
            }
            
            # El listado y descarga de adjuntos van contra adjunto.mercadopublico.cl usando user_key
            list_url = f"{CompraAgilService.BASE_URL_ADJUNTO}/adjunto-compra-agil/v1/adjuntos-compra-agil/listar/{codigo}"
            print(f"[TRACE] Solicitando lista de adjuntos a URL: {list_url}")
            
            archivos_data = []
            try:
                res_list = await client.get(list_url, headers=headers_adjunto)
                print(f"[TRACE] Respuesta adjuntos recibida. Status Code: {res_list.status_code}")
                
                if res_list.status_code != 200:
                    print("==== ERROR LISTAR ADJUNTOS ====")
                    print(f"[ERROR] STATUS: {res_list.status_code}")
                    print(f"[ERROR] REASON: {res_list.text}")
                    print("[WARNING] Continuando el proceso únicamente con la Ficha capturada.")
                else:
                    try:
                        payload_list = res_list.json()
                        payload_dict = payload_list.get("payload") or {}
                        
                        if isinstance(payload_dict.get("Data"), list):
                            archivos_data = payload_dict["Data"]
                        elif isinstance(payload_dict.get("files"), list):
                            archivos_data = payload_dict["files"]
                        else:
                            if not upload_files:
                                return ApiResponse.fail(message="Estructura de payload de adjuntos desconocida desde Mercado Público.")
                            else:
                                print("[TRACE] No se encontraron adjuntos adicionales en el payload.")
                    except Exception as e:
                        print(f"[ERROR] No se pudo parsear el JSON de la respuesta: {e}")
                        
            except Exception as e:
                print(f"[ERROR] Falló la conexión con la API de adjuntos: {e}")
                print("[WARNING] Procediendo solo con la Ficha capturada.")
            
            if not archivos_data and not upload_files:
                return ApiResponse.fail(message="No se encontraron archivos ni ficha para esta Licitación.")

            for arch in archivos_data:
                # Extraer uuid y nombre soportando ambos formatos (Url/NombreArchivo o id/nombreArchivo)
                uuid = arch.get("Url") or arch.get("id")
                nombre_base = arch.get("NombreArchivo") or arch.get("nombreArchivo")
                
                if not uuid:
                    print(f"[ERROR] Archivo sin identificador (uuid): {arch}")
                    continue
                    
                nombre = nombre_base or f"adjunto_{uuid}.pdf"
                
                down_url = f"{CompraAgilService.BASE_URL_ADJUNTO}/adjunto-compra-agil/v1/adjuntos-compra-agil/descargar/{uuid}"
                print(f"[TRACE] Descargando adjunto: {nombre} ({uuid}) -> {down_url}")
                
                res_down = await client.get(down_url, headers=headers_adjunto)
                print(f"[TRACE] Resultado descarga {nombre}: Status {res_down.status_code}")
                
                if res_down.status_code == 200:
                    content = res_down.content
                    
                    # File Name fallback correction because sometimes there is no response JSON to parse it
                    if not nombre or nombre.strip() == "":
                        nombre = f"adjunto_{uuid}.pdf"
                    
                    archivos_procesados.append(ArchivoCompraAgilResponse(nombre=nombre, ruta="MEMORIA", uuid=uuid))
                    
                    # Convert to FastAPI UploadFile for LicitacionNewService
                    file_like = io.BytesIO(content)
                    upload_file = UploadFile(file=file_like, filename=nombre)
                    # Hack for Starlette < 0.28 if size is needed or just rely on read()
                    upload_files.append(upload_file)

        if not upload_files:
             return ApiResponse.fail(message="No se pudo descargar ningún archivo válido.")

        # Re-use the Licitacion creation logic to trigger ETL
        new_lic_response = await LicitacionNewService.process(f"Compra Ágil {codigo}", upload_files, 'COMPRA_AGIL')
        
        if not new_lic_response.success:
            return ApiResponse.fail(message=f"Error al enlazar a Licitación: {new_lic_response.message}")
            
        return ApiResponse.ok(
            data=ImportCompraAgilResponse(
                codigo=codigo,
                licitacion_id=str(new_lic_response.data.id),
                mensaje="Compra Ágil importada y procesada correctamente",
                archivos_descargados=archivos_procesados
            ),
            message="Importación Iniciada."
        )
