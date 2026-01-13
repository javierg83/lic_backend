# ======================================================================
# MODEL
# ======================================================================

from typing import Generic, TypeVar, Optional
from pydantic import BaseModel
from typing import List
from datetime import date

T = TypeVar("T")
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    message: str
    data: Optional[T] = None
    error: Optional[str] = None

class DemoListIn(BaseModel):
    pass  # Request vacío


class DemoListOut(BaseModel):
    id: int
    nombre: str
    valor: float
    fecha: date



# ======================================================================
# ROUTER
# ======================================================================

from fastapi import APIRouter

router = APIRouter()

@router.post("/list", response_model=ApiResponse[List[DemoListOut]])
async def demo_list(data: DemoListIn):
#async def demo_list(data: DemoListIn, user: dict = Depends(auth_required)):    # seguridad JWT    
    return DemoListService.process(data)    


# ======================================================================
# SERVICE
# ======================================================================


class DemoListService:

    @staticmethod
    def process(data: DemoListIn) -> ApiResponse[List[DemoListOut]]:
        try:

            # Ahora 'data' es un objeto y 'data.id' un atributo
            #print(f'data con ID: {data.id}')            
  
            items = [
                DemoListOut(id=1,nombre="nombre1",valor=1.1,fecha=date(2001,10,21)),
                DemoListOut(id=2,nombre="nombre2",valor=2.2,fecha=date(2002,10,22))
            ]

            return ApiResponse(
                success=True,
                message="Listado obtenido correctamente",
                data=items
            )

        except Exception as e:
            return ApiResponse(
                success=False,
                message="Error al obtener listado de licitaciones privadas",
                error=str(e)
            )