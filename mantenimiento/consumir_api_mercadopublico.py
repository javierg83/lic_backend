import requests
import json
from typing import Optional, Dict, Any

class MercadoPublicoAPI:
    """
    Cliente para consumir la API de Mercado Público.
    Basado en la documentación oficial de api.mercadopublico.cl.
    """
    
    BASE_URL = "https://api.mercadopublico.cl/servicios/v1/publico/licitaciones.json"
    
    def __init__(self, ticket: str = "2A814D73-C359-4EF8-BC18-39D5C3A2D34E"):
        """
        Inicializa el cliente de la API con el ticket proporcionado.
        :param ticket: Ticket de acceso a la API.
        """
        self.ticket = ticket

    def _make_request(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Método interno para realizar la petición GET a la API.
        
        :param params: Diccionario de parámetros GET.
        :return: Diccionario con la respuesta JSON, o None si ocurre un error.
        """
        # Se agrega siempre el ticket a los parámetros de la petición
        params['ticket'] = self.ticket
        
        try:
            print(f"[{params.get('codigo', 'General')}] Consultando API con parámetros: {params}")
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as error_http:
            print(f"Error HTTP ocurrido: {error_http}")
        except requests.exceptions.ConnectionError as error_conn:
            print(f"Error de conexión: {error_conn}")
        except requests.exceptions.Timeout as error_timeout:
            print(f"Timeout en la petición: {error_timeout}")
        except requests.exceptions.RequestException as error_req:
            print(f"Error general en la petición: {error_req}")
        
        return None

    def get_licitacion_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por {código} de licitación. Ejemplo: 1509-5-L114.
        El formato de respuesta entregado proporciona información detallada de la Licitación.
        """
        return self._make_request({"codigo": codigo})

    def get_licitaciones_hoy(self) -> Optional[Dict[str, Any]]:
        """
        Consulta por todos los estados del día actual.
        Obtendrá información básica de las Licitaciones publicadas en el día.
        """
        return self._make_request({})

    def get_licitaciones_por_fecha(self, fecha: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por todos los estados de una {fecha} en particular.
        
        :param fecha: Formato ddmmaaaa (ej. 02022014)
        """
        return self._make_request({"fecha": fecha})

    def get_licitaciones_activas(self) -> Optional[Dict[str, Any]]:
        """
        Consulta por estado "activas". 
        Muestra todas las licitaciones publicadas al día de realizada la consulta.
        """
        return self._make_request({"estado": "activas"})

    def get_licitaciones_por_estado_fecha(self, estado: str, fecha: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por {estado} en una {fecha} en particular.
        
        :param estado: Estados posibles (activas, publicada, cerrada, desierta, adjudicada, revocada, suspendida, todos)
        :param fecha: Formato ddmmaaaa (ej. 02022014)
        """
        return self._make_request({"estado": estado, "fecha": fecha})

    def get_licitaciones_por_estado_hoy(self, estado: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por {estado} del día actual.
        """
        return self._make_request({"estado": estado})

    def get_licitaciones_por_organismo(self, codigo_organismo: str, fecha: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por {código} de Organismo Público en una {fecha} en particular.
        
        :param codigo_organismo: Ejemplo: 6945
        :param fecha: Formato ddmmaaaa (ej. 02022014)
        """
        return self._make_request({"CodigoOrganismo": codigo_organismo, "fecha": fecha})

    def get_licitaciones_por_proveedor(self, codigo_proveedor: str, fecha: str) -> Optional[Dict[str, Any]]:
        """
        Consulta por {código} de Proveedor en una {fecha} en particular.
        
        :param codigo_proveedor: Ejemplo: 17793
        :param fecha: Formato ddmmaaaa (ej. 02022014)
        """
        return self._make_request({"CodigoProveedor": codigo_proveedor, "fecha": fecha})

# --- Ejemplo de uso y prueba ---
if __name__ == "__main__":
    print("Iniciando pruebas de la API Mercado Público...")
    
    # El ticket proporcionado por el usuario
    ticket_usuario = "2A814D73-C359-4EF8-BC18-39D5C3A2D34E"
    api_cliente = MercadoPublicoAPI(ticket=ticket_usuario)
    
    # 1. Probar obtener licitaciones del día actual
    print("\n--- Obteniendo licitaciones general para hoy ---")
    resultados_hoy = api_cliente.get_licitaciones_hoy()
    if resultados_hoy:
        cantidad = resultados_hoy.get("Cantidad", 0)
        print(f"✅ Éxito: Se obtuvieron {cantidad} licitaciones para el día de hoy.")
        
        # 2. Si hay resultados, probamos consultar el detalle por el código de la primera
        if cantidad > 0:
            licitaciones = resultados_hoy.get("Listado", [])
            if licitaciones:
                primer_codigo = licitaciones[0].get("CodigoExterno")
                print(f"\n--- Obteniendo detalle de la primera licitación ({primer_codigo}) ---")
                detalle = api_cliente.get_licitacion_por_codigo(primer_codigo)
                if detalle and detalle.get("Cantidad", 0) > 0:
                    nombre = detalle.get("Listado", [])[0].get("Nombre", "Sin Nombre")
                    print(f"✅ Éxito: Detalle obtenido - Nombre Licitación: {nombre}")
                else:
                    print("❌ Fallo obteniendo detalle o no se encontró.")
    else:
        print("❌ Fallo al obtener licitaciones para el día de hoy.")
    
    # 3. Probar obtener licitaciones activas general (opcional)
    # print("\n--- Obteniendo licitaciones activas ---")
    # activas = api_cliente.get_licitaciones_activas()
    # if activas:
    #     print(f"✅ Éxito: Se obtuvieron {activas.get('Cantidad', 0)} licitaciones activas.")
