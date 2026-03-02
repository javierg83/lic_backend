from fastapi import APIRouter
from src.core.responses import ApiResponse
from .service import DashboardService
from .schemas import DashboardResponse

router = APIRouter(prefix="/control-room", tags=["Control Room Dashboard"])

@router.get("/resumen", response_model=ApiResponse)
def get_control_room_resumen():
    try:
        data = DashboardService.get_resumen()
        return ApiResponse.ok(message="Dashboard data retrieved", data=data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ApiResponse.fail(message="Error retrieving dashboard data", error=str(e))
