import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext

from database import get_db
from schemas import EmpleadoCreate, EmpleadoUpdate
from routers.auth import verificar_token

router = APIRouter()
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("/")
def listar_empleados(
    db: Session = Depends(get_db),
    user: dict = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador", "supervisor"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    rows = db.execute(text("""
        SELECT id, cedula, nombre, apellidos, rol, estado, salario_hora, fecha_ingreso,
               telefono, correo
        FROM empleados
        ORDER BY apellidos
    """)).fetchall()

    return [dict(r._mapping) for r in rows]

@router.post("/")
def crear_empleado(
    data: EmpleadoCreate,
    db: Session = Depends(get_db),
    user: dict = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    eid = str(uuid.uuid4())
    try:
        db.execute(text("""
            INSERT INTO empleados
              (id, cedula, nombre, apellidos, rol, estado, salario_hora, fecha_ingreso,
               telefono, correo, password_hash)
            VALUES
              (:id, :c, :n, :a, :r, :e, :sh, :fi, :t, :co, :pw)
        """), {
            "id": eid,
            "c": data.cedula,
            "n": data.nombre,
            "a": data.apellidos,
            "r": data.rol.value if hasattr(data.rol, 'value') else data.rol,
            "e": data.estado,
            "sh": data.salario_hora,
            "fi": data.fecha_ingreso,
            "t": data.telefono,
            "co": data.correo,
            "pw": pwd.hash(data.password)
        })
        db.commit()
        return {"id": eid, "ok": True}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Cédula ya existe")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{empleado_id}")
def actualizar_empleado(
    empleado_id: str,
    data: EmpleadoUpdate,
    db: Session = Depends(get_db),
    user: dict = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    updates = {}
    if data.nombre: updates["nombre"] = data.nombre
    if data.apellidos: updates["apellidos"] = data.apellidos
    if data.rol: updates["rol"] = data.rol.value if hasattr(data.rol, 'value') else data.rol
    if data.estado: updates["estado"] = data.estado
    if data.salario_hora is not None: updates["salario_hora"] = data.salario_hora
    if data.telefono: updates["telefono"] = data.telefono
    if data.correo: updates["correo"] = data.correo
    if data.fecha_ingreso: updates["fecha_ingreso"] = data.fecha_ingreso
    if data.password: updates["password_hash"] = pwd.hash(data.password)

    if not updates:
        raise HTTPException(status_code=400, detail="Sin datos para actualizar")

    set_clause = ", ".join([f"{k} = :{k}" for k in updates.keys()])
    updates["id"] = empleado_id

    db.execute(text(f"UPDATE empleados SET {set_clause} WHERE id = :id"), updates)
    db.commit()
    return {"ok": True}

@router.delete("/{empleado_id}")
def eliminar_empleado(
    empleado_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(verificar_token)
):
    if user["rol"] != "super_admin":
        raise HTTPException(status_code=403, detail="Solo super_admin")

    db.execute(text("UPDATE empleados SET estado = 'inactivo' WHERE id = :id"), {"id": empleado_id})
    db.commit()
    return {"ok": True}
