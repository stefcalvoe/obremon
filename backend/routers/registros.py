import base64, uuid
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db, date_today_expr, bool_true
from schemas import CheckInRequest, RegistroOut, EstadoValidacion
from routers.auth import verificar_token
from utils.gps import dentro_del_radio

router = APIRouter()

@router.post("/checkin", response_model=RegistroOut)
def check_in(
    data: CheckInRequest,
    db:   Session = Depends(get_db),
    user: dict    = Depends(verificar_token)
):
    empleado_id = uuid.UUID(user["sub"])

    # 1. Obtener turno activo del empleado para hoy
    hoy = date.today().strftime('%A').lower()
    turno = db.execute(text("""
        SELECT t.id, t.hora_entrada, t.hora_salida, t.tolerancia_min,
               p.latitud, p.longitud, p.radio_metros
        FROM turnos t
        JOIN puntos p ON p.id = t.punto_id
        WHERE t.empleado_id = :eid
          AND t.activo = TRUE
          AND :hoy = ANY(t.dias::text[])
          AND (t.vigente_hasta IS NULL OR t.vigente_hasta >= CURRENT_DATE)
        LIMIT 1
    """), {"eid": empleado_id, "hoy": hoy}).fetchone()

    if not turno:
        raise HTTPException(status_code=404, detail="No hay turno asignado para hoy")

    # 2. Validar GPS
    gps_ok, distancia = dentro_del_radio(
        data.latitud, data.longitud,
        turno.latitud, turno.longitud,
        turno.radio_metros
    )

    # 3. Validar llegada tarde (solo en entrada)
    estado = EstadoValidacion.valido
    if data.tipo == "entrada":
        ahora = datetime.now().time()
        from datetime import timedelta
        limite = (
            datetime.combine(date.today(), turno.hora_entrada)
            + timedelta(minutes=turno.tolerancia_min)
        ).time()
        if ahora > limite:
            estado = EstadoValidacion.tarde

    if not gps_ok:
        estado = EstadoValidacion.fuera_de_zona

    # 4. Guardar foto en Supabase Storage (opcional)
    foto_url = None
    if data.foto_base64:
        foto_url = f"fotos/{empleado_id}/{datetime.now().isoformat()}.jpg"

    if not data.foto_base64 and estado == EstadoValidacion.valido:
        estado = EstadoValidacion.sin_foto

    # 5. Insertar registro
    registro_id = uuid.uuid4()
    db.execute(text("""
        INSERT INTO registros (
            id, empleado_id, turno_id, tipo, timestamp_registro,
            latitud_real, longitud_real, distancia_metros, gps_valido,
            foto_url, facial_valido, estado_validacion
        ) VALUES (
            :id, :emp, :turno, :tipo, NOW(),
            :lat, :lon, :dist, :gps,
            :foto, :facial, :estado
        )
    """), {
        "id":     str(registro_id),
        "emp":    str(empleado_id),
        "turno":  str(turno.id),
        "tipo":   data.tipo,
        "lat":    data.latitud,
        "lon":    data.longitud,
        "dist":   distancia,
        "gps":    gps_ok,
        "foto":   foto_url,
        "facial": True if data.foto_base64 else False,
        "estado": estado.value,
    })
    db.commit()

    return RegistroOut(
        id=str(registro_id),
        empleado_id=str(empleado_id),
        tipo=data.tipo,
        timestamp_registro=datetime.now(),
        gps_valido=gps_ok,
        facial_valido=bool(data.foto_base64),
        distancia_metros=distancia,
        estado_validacion=estado,
        nota_manual=None,
    )

@router.get("/hoy")
def registros_hoy(
    db:   Session = Depends(get_db),
    user: dict    = Depends(verificar_token)
):
    empleado_id = user["sub"]
    hoy = date_today_expr()
    rows = db.execute(text(f"""
        SELECT id, empleado_id, tipo, timestamp_registro, estado_validacion, nota_manual,
               gps_valido, facial_valido, distancia_metros
        FROM registros
        WHERE empleado_id = :eid
          AND DATE(timestamp_registro) = {hoy}
        ORDER BY timestamp_registro ASC
    """), {"eid": empleado_id}).fetchall()
    return [dict(r._mapping) for r in rows]

@router.get("/dashboard")
def dashboard_asistencia(
    db:   Session = Depends(get_db),
    user: dict    = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador", "supervisor"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    hoy = date_today_expr()
    activo = bool_true()
    rows = db.execute(text(f"""
        SELECT
            e.id AS empleado_id,
            e.nombre || ' ' || e.apellidos AS nombre_completo,
            t.hora_entrada,
            t.hora_salida,
            r_in.timestamp_registro  AS hora_checkin,
            r_out.timestamp_registro AS hora_checkout,
            COALESCE(r_in.estado_validacion, 'pendiente') AS estado_validacion,
            COALESCE(p.nombre, 'Sin punto') AS punto
        FROM empleados e
        LEFT JOIN turnos t ON t.empleado_id = e.id AND t.activo = {activo}
        LEFT JOIN puntos p ON p.id = t.punto_id
        LEFT JOIN registros r_in  ON r_in.empleado_id  = e.id AND r_in.tipo  = 'entrada'
            AND DATE(r_in.timestamp_registro)  = {hoy}
        LEFT JOIN registros r_out ON r_out.empleado_id = e.id AND r_out.tipo = 'salida'
            AND DATE(r_out.timestamp_registro) = {hoy}
        WHERE e.estado = 'activo'
        ORDER BY e.apellidos
    """)).fetchall()

    return [dict(r._mapping) for r in rows]

@router.post("/manual")
def registro_manual(
    data: dict,
    db:   Session = Depends(get_db),
    user: dict    = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador", "supervisor"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    rid = str(uuid.uuid4())
    ts = data.get("timestamp") or datetime.now().isoformat()

    db.execute(text("""
        INSERT INTO registros (id, empleado_id, tipo, timestamp_registro, estado_validacion, nota_manual)
        VALUES (:id, :emp, :tipo, :ts, 'manual', :nota)
    """), {
        "id": rid,
        "emp": data["empleado_id"],
        "tipo": data["tipo"],
        "ts": ts,
        "nota": data.get("nota", "Registro manual admin")
    })
    db.commit()
    return {"ok": True, "id": rid}

@router.put("/{registro_id}/ajuste")
def ajuste_manual(
    registro_id: str,
    nota:        str,
    db:          Session = Depends(get_db),
    user:        dict    = Depends(verificar_token)
):
    if user["rol"] not in ("super_admin", "coordinador"):
        raise HTTPException(status_code=403, detail="Sin permisos")

    db.execute(text("""
        UPDATE registros
        SET estado_validacion = 'manual',
            nota_manual       = :nota,
            ajustado_por      = :admin
        WHERE id = :rid
    """), {"nota": nota, "admin": user["sub"], "rid": registro_id})
    db.commit()
    return {"ok": True, "mensaje": "Registro ajustado"}
