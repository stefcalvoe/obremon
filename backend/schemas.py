from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional

class RolSistema(str, Enum):
    super_admin = "super_admin"
    coordinador = "coordinador"
    supervisor = "supervisor"
    guardia = "guardia"

class EstadoValidacion(str, Enum):
    valido = "valido"
    tarde = "tarde"
    fuera_de_zona = "fuera_de_zona"
    sin_foto = "sin_foto"
    manual = "manual"
    pendiente = "pendiente"

class LoginRequest(BaseModel):
    cedula: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id: str = ""
    nombre: str = ""
    apellidos: str = ""
    rol: str = ""

class EmpleadoCreate(BaseModel):
    cedula: str
    nombre: str
    apellidos: str
    rol: RolSistema
    estado: str = "activo"
    salario_hora: Optional[float] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: str
    fecha_ingreso: str

class EmpleadoUpdate(BaseModel):
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    rol: Optional[RolSistema] = None
    estado: Optional[str] = None
    salario_hora: Optional[float] = None
    telefono: Optional[str] = None
    correo: Optional[EmailStr] = None
    password: Optional[str] = None
    fecha_ingreso: Optional[str] = None

class CheckInRequest(BaseModel):
    tipo: str
    latitud: float
    longitud: float
    foto_base64: Optional[str] = None

class RegistroOut(BaseModel):
    id: str
    empleado_id: str
    tipo: str
    timestamp_registro: datetime
    gps_valido: bool
    facial_valido: bool
    distancia_metros: float
    estado_validacion: EstadoValidacion
    nota_manual: Optional[str] = None
