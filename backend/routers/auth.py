from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from database import get_db
from schemas import LoginRequest, TokenResponse

router = APIRouter()

SECRET_KEY = __import__('os').getenv("SECRET_KEY", "cambiar_por_clave_segura_en_produccion")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = __import__('datetime').datetime.utcnow() + expires_delta
    else:
        expire = __import__('datetime').datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verificar_token(token: str = __import__('fastapi').Header(None)):
    from fastapi.security import HTTPBearer, HTTPAuthCredentials
    if not token:
        raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    row = db.execute(text("""
        SELECT id, nombre, apellidos, rol, password_hash
        FROM empleados
        WHERE cedula = :c AND estado = 'activo'
    """), {"c": data.cedula}).fetchone()

    if not row or not pwd_context.verify(data.password, row.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token(
        data={"sub": str(row.id), "rol": row.rol}
    )

    return TokenResponse(
        access_token=token,
        id=str(row.id),
        nombre=row.nombre,
        apellidos=row.apellidos,
        rol=row.rol
    )
