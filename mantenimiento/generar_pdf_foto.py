import os
import time
import base64
from urllib.parse import urlparse, parse_qs
from pathlib import Path
from datetime import datetime
from io import BytesIO

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image

def get_code_from_url(url):
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if 'code' in qs:
        return qs['code'][0]
    
    filename_safe = "".join([c if c.isalnum() else "_" for c in url]).strip("_")[0:30]
    return filename_safe

def generar_pdf_desde_foto():
    url = input("Ingrese la URL para extraer (ej. https://buscador.mercadopublico.cl/ficha?code=3724-9-COT26): ").strip()
    if not url:
        print("URL inválida.")
        return

    code = get_code_from_url(url)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if "mercadopublico" in url:
        prefix = "foto"
    else:
        prefix = "fotoweb"
        
    nombre_archivo = f"{prefix}_{code}_{timestamp}.pdf"
    
    # Path relative to lic_backend/productos/codigo
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_base = Path(base_dir) / "productos" / code
    ruta_base.mkdir(parents=True, exist_ok=True)
    
    ruta_pdf = ruta_base / nombre_archivo

    print(f"\nGenerando PDF (modo Foto Completa) para: {url}")
    print(f"Directorio de destino: {ruta_base}")
    print(f"Archivo de destino: {ruta_pdf}\n")

    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--disable-dev-shm-usage')

    # Anti-bot bypass configuration
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    print("Iniciando navegador...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    # Execute CDP command to override navigator.webdriver if necessary
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })

    try:
        print("Cargando página...")
        driver.get(url)
        
        print("Esperando 10 segundos para el contenido inicial...")
        time.sleep(10) 
        
        print("Haciendo scroll para asegurar lazy loading...")
        total_height = driver.execute_script("return document.body.scrollHeight")
        viewport_height = driver.execute_script("return window.innerHeight")
        
        current_scroll = 0
        while current_scroll < total_height:
            driver.execute_script(f"window.scrollTo(0, {current_scroll});")
            time.sleep(1.5)  # Tiempo de espera mayor para que la red responda por cada bloque
            current_scroll += viewport_height
            # Reevaluar la altura ya que puede aumentar con el scroll
            total_height = driver.execute_script("return document.body.scrollHeight")
            
        driver.execute_script(f"window.scrollTo(0, {total_height});")
        print("Final del documento alcanzado. Esperando 5 segundos para render final...")
        time.sleep(5) 
        
        # Ocultar scrollbars u otros elementos fastidiosos antes de la foto
        driver.execute_script("""
            document.body.style.overflow = 'hidden';
        """)
        
        # Obtener las dimensiones exactas usando el protocolo CDP
        print("Calculando dimensiones reales de la página...")
        metrics = driver.execute_cdp_cmd("Page.getLayoutMetrics", {})
        width = metrics['contentSize']['width']
        height = metrics['contentSize']['height']
        
        # Asegurarnos de que el viewport cubra todo
        driver.set_window_size(width, height)
        time.sleep(2)
        
        print(f"Tomando foto a pantalla completa (Resolución: {width}x{height}px)...")
        screenshot_config = {
            "format": "png",
            "captureBeyondViewport": True,
            "clip": {
                "width": width,
                "height": height,
                "x": 0,
                "y": 0,
                "scale": 1
            }
        }
        
        result = driver.execute_cdp_cmd("Page.captureScreenshot", screenshot_config)
        
        print("Convirtiendo imagen a formato PDF...")
        # Cargar los datos RAW base64 como una imagen usando Pillow
        img = Image.open(BytesIO(base64.b64decode(result['data'])))
        
        # Convertir a RGB (Los PDFs no soportan el canal alfa/transparencia de igual forma y Pillow lo requiere en RGB)
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        # Guardar como PDF
        img.save(ruta_pdf, "PDF", resolution=100.0)
        
        print(f"\n✅ PDF (desde foto completa) generado correctamente en:\n{ruta_pdf}")
        
    except Exception as e:
        print(f"\n❌ Error al generar el PDF fotográfico: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    generar_pdf_desde_foto()
