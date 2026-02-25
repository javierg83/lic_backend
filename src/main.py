from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.features.auth.controller import router as auth_router
from src.features.home.controller import router as main_router
from src.core.responses import ApiResponse

app = FastAPI()

# 🔥 Redirect global REAL
@app.get("/")
def root():
    return RedirectResponse(url="/main")

# -----------------------------
# CORS para permitir Angular
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Routers
# -----------------------------
app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(main_router, prefix="/main", tags=["Main"])

from src.features.demo.router import router as demo_router
from src.features.licitaciones.router import router as licitaciones_router

app.include_router(demo_router, prefix="/demo", tags=["Demo"])
app.include_router(licitaciones_router, prefix="/licitaciones", tags=["Licitaciones"])

"""
# para generar seguridad

from src.features.auth.dependencies import auth_required

app.include_router(
    demo_router, 
    prefix="/demo", 
    tags=["Demo"], 
    dependencies=[Depends(auth_required)] # <--- Aquí
)
"""


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # if exc.status_code == 404 and request.method == "GET":
    #     return RedirectResponse(url="/main")
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ApiResponse.fail(
            message=str(exc.detail),
            error=f"HTTP {exc.status_code}"
        ).model_dump()
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ApiResponse.fail(
            message="Error interno del servidor",
            error=str(exc)
        ).model_dump()
    )