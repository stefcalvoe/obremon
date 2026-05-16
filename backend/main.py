from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from database import engine, SessionLocal, IS_SQLITE
from routers.auth import router as auth_router
from routers.empleados import router as empleados_router
from routers.registros import router as registros_router

app = FastAPI(title="OBREMON API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(empleados_router, prefix="/empleados", tags=["empleados"])
app.include_router(registros_router, prefix="/registros", tags=["registros"])

@app.on_event("startup")
def startup_event():
    if IS_SQLITE:
        from init_db import init_db
        init_db()

@app.get("/")
def root():
    return {"message": "OBREMON API", "status": "online"}

@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
