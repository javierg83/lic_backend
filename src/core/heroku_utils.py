import os
import json
import urllib.request
import threading

def _send_scale_request(quantity: int):
    api_key = os.getenv("HEROKU_API_KEY")
    app_name = os.getenv("HEROKU_APP_NAME_WORKER")

    if not api_key or not app_name:
        print(f"💡 [MOCK HEROKU] Variables de entorno faltantes. Simulando solicitud de escalado a Heroku: Dyno escalado a {quantity}.")
        return

    url = f"https://api.heroku.com/apps/{app_name}/formation/worker"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/vnd.heroku+json; version=3",
        "Content-Type": "application/json"
    }
    data = json.dumps({"quantity": quantity}).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data, headers=headers, method="PATCH")
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status in (200, 201):
                print(f"✅ [HEROKU API] Worker escalado a {quantity} exitosamente.")
            else:
                print(f"⚠️ [HEROKU API] Respuesta inesperada escalando a {quantity}: {response.status}")
    except Exception as e:
        print(f"❌ [HEROKU API] Error al escalar worker a {quantity}: {e}")

def scale_worker_dyno(quantity: int = 1, run_in_background: bool = True):
    """
    Escala el dyno worker de Heroku a la cantidad especificada.
    Por defecto lo corre en un thread separado para no bloquear el flujo principal.
    """
    if run_in_background:
        threading.Thread(target=_send_scale_request, args=(quantity,), daemon=True).start()
    else:
        _send_scale_request(quantity)
