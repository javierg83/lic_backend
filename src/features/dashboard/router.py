from fastapi import APIRouter, Depends
from src.core.responses import ApiResponse
from src.features.auth.dependencies import auth_required
from .service import DashboardService
from .schemas import DashboardResponse

router = APIRouter(prefix="/control-room", tags=["Control Room Dashboard"])

@router.get("/resumen", response_model=ApiResponse)
def get_control_room_resumen(user_data: dict = Depends(auth_required)):
    try:
        # Admin ve todos los datos; cliente ve solo los suyos
        rol = user_data.get("rol")
        cliente_id = user_data.get("cliente_id") if rol != "admin" else None
        data = DashboardService.get_resumen(cliente_id=cliente_id)
        return ApiResponse.ok(message="Dashboard data retrieved", data=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ApiResponse.fail(message="Error retrieving dashboard data", error=str(e))
