from datetime import date
from src.core.responses import ApiResponse
from .schemas import DemoShowIn, DemoShowOut

class DemoShowService:
    @staticmethod
    def process(data: DemoShowIn) -> ApiResponse[DemoShowOut]:
        try:
            # Simulación de obtención de datos
            item = DemoShowOut(
                licitacion_nombre=f"Licitación de Prueba {data.licitacion_id}",
                licitacion_encargado="Juan Pérez",
                licitacion_fecha_inicio=date(2024, 1, 1),
                licitacion_fecha_termino=date(2024, 12, 31),
                licitacion_fecha_creacion=date(2023, 11, 15)
            )

            return ApiResponse(
                success=True,
                message="Licitación obtenida correctamente",
                data=item
            )
        except Exception as e:
            return ApiResponse(
                success=False,
                message="Error al obtener la licitación",
                error=str(e)
            )
