from datetime import date
from typing import List
from src.core.responses import ApiResponse
from .schemas import DemoListIn, DemoListOut

class DemoListService:
    @staticmethod
    def process(data: DemoListIn) -> ApiResponse[List[DemoListOut]]:
        try:
            items = [
                DemoListOut(id=1, nombre="nombre1", valor=1.1, fecha=date(2001, 10, 21)),
                DemoListOut(id=2, nombre="nombre2", valor=2.2, fecha=date(2002, 10, 22))
            ]

            return ApiResponse(
                success=True,
                message="Listado obtenido correctamente",
                data=items
            )
        except Exception as e:
            return ApiResponse(
                success=False,
                message="Error al obtener listado demo",
                error=str(e)
            )
