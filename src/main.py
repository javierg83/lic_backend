from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import RedirectResponse

from src.api.user_auth import router as auth_router
from src.api.home import router as main_router

app = FastAPI()

print('entro aca')


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

from src.api.demo.routes import router as demo_router
app.include_router(demo_router, prefix="/demo", tags=["Demo"])

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc):
    if exc.status_code == 404 and request.method == "GET":
        return RedirectResponse(url="/main")
    raise exc