import os
import uuid
from datetime import date
from sqlalchemy import text
from passlib.context import CryptContext
from database import SessionLocal, IS_SQLITE

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    if not IS_SQLITE:
        return

    db = SessionLocal()

    schema = """
    CREATE TABLE IF NOT EXISTS empleados (
        id TEXT PRIMARY KEY,
        cedula TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        apellidos TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'guardia',
        estado TEXT NOT NULL DEFAULT 'activo',
        salario_hora REAL,
        fecha_ingreso TEXT,
        telefono TEXT,
        correo TEXT,
        password_hash TEXT NOT NULL DEFAULT '',
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS puntos (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        latitud REAL NOT NULL,
        longitud REAL NOT NULL,
        radio_metros REAL NOT NULL DEFAULT 50,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS turnos (
        id TEXT PRIMARY KEY,
        empleado_id TEXT NOT NULL REFERENCES empleados(id),
        punto_id TEXT NOT NULL REFERENCES puntos(id),
        hora_entrada TIME NOT NULL,
        hora_salida TIME NOT NULL,
        tolerancia_min INTEGER DEFAULT 5,
        dias TEXT,
        activo BOOLEAN DEFAULT TRUE,
        vigente_desde TEXT,
        vigente_hasta TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS registros (
        id TEXT PRIMARY KEY,
        empleado_id TEXT NOT NULL REFERENCES empleados(id),
        turno_id TEXT REFERENCES turnos(id),
        tipo TEXT NOT NULL,
        timestamp_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        latitud_real REAL,
        longitud_real REAL,
        distancia_metros REAL,
        gps_valido BOOLEAN,
        foto_url TEXT,
        facial_valido BOOLEAN,
        estado_validacion TEXT,
        nota_manual TEXT,
        ajustado_por TEXT,
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS periodos_planilla (
        id TEXT PRIMARY KEY,
        nombre TEXT NOT NULL,
        fecha_inicio DATE NOT NULL,
        fecha_fin DATE NOT NULL,
        estado TEXT DEFAULT 'abierto',
        creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS planilla_detalle (
        id TEXT PRIMARY KEY,
        periodo_id TEXT NOT NULL REFERENCES periodos_planilla(id) ON DELETE CASCADE,
        empleado_id TEXT NOT NULL REFERENCES empleados(id) ON DELETE CASCADE,
        horas_ordinarias REAL DEFAULT 0,
        horas_extra REAL DEFAULT 0,
        horas_nocturnas REAL DEFAULT 0,
        dias_ausente INTEGER DEFAULT 0,
        salario_base REAL DEFAULT 0,
        monto_extra REAL DEFAULT 0,
        total_pagar REAL DEFAULT 0,
        calculado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE INDEX IF NOT EXISTS idx_registros_empleado ON registros(empleado_id);
    CREATE INDEX IF NOT EXISTS idx_registros_timestamp ON registros(timestamp_registro);
    CREATE INDEX IF NOT EXISTS idx_turnos_empleado ON turnos(empleado_id);
    CREATE INDEX IF NOT EXISTS idx_planilla_periodo ON planilla_detalle(periodo_id, empleado_id);
    """

    try:
        for statement in schema.split(';'):
            if statement.strip():
                db.execute(text(statement))
        db.commit()

        # Crear admin inicial
        existe = db.execute(text("SELECT id FROM empleados WHERE cedula = ?"), ("000000000",)).fetchone()
        if not existe:
            eid = str(uuid.uuid4())
            db.execute(text("""
                INSERT INTO empleados
                  (id, cedula, nombre, apellidos, rol, estado, salario_hora, fecha_ingreso, password_hash)
                VALUES
                  (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (
                eid, "000000000", "Admin", "OBREMON",
                "super_admin", "activo", 0, str(date.today()),
                pwd.hash("obremon2025")
            ))
            db.commit()
            print("✓ Admin creado: 000000000 / obremon2025")
        else:
            print("✓ Admin ya existe")
    except Exception as e:
        db.rollback()
        print(f"✗ Error inicializando BD: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
