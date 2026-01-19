from src.core.responses import ApiResponse
from .schemas import DemoNewIn, DemoNewOut
from datetime import date

class DemoNewService:
    @staticmethod
    def process(data: DemoNewIn) -> ApiResponse[DemoNewOut]:
        try:
            # Mejora: Validación mínima vital
            today = date.today()
            calculated_age = today.year - data.fecha_nacimiento.year - ((today.month, today.day) < (data.fecha_nacimiento.month, data.fecha_nacimiento.day))
            
            if calculated_age != data.edad:
                return ApiResponse(
                    success=False,
                    error=f"La edad proporcionada ({data.edad}) no coincide con la fecha de nacimiento ({calculated_age} años calculados).",
                    message="Validation Error"
                )
            # Simulación de creación
            result = DemoNewOut(
                id=99,  # ID simulado
                nombre=data.nombre,
                success=True
            )

            return ApiResponse(
                success=True,
                message="Elemento creado correctamente",
                data=result
            )
        except Exception as e:
            return ApiResponse(
                success=False,
                message="Error al procesar la solicitud /new",
                error=str(e)
            )
