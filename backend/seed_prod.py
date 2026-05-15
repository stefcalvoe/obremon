"""
Ejecutar UNA SOLA VEZ en producción para crear el admin inicial:
  python seed_prod.py
"""
import os
import uuid
from datetime import date
from sqlalchemy import text
from passlib.context import CryptContext
from database import SessionLocal

pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
db  = SessionLocal()

CEDULA   = os.getenv("ADMIN_CEDULA",   "000000000")
PASSWORD = os.getenv("ADMIN_PASSWORD", "obremon2025")
NOMBRE   = os.getenv("ADMIN_NOMBRE",   "Admin")
APELLIDO = os.getenv("ADMIN_APELLIDO", "OBREMON")

try:
    existe = db.execute(text("SELECT id FROM empleados WHERE cedula = :c"), {"c": CEDULA}).fetchone()
    if existe:
        print(f"Admin {CEDULA} ya existe.")
    else:
        eid = str(uuid.uuid4())
        db.execute(text("""
            INSERT INTO empleados
              (id, cedula, nombre, apellidos, rol, estado, salario_hora, fecha_ingreso, password_hash)
            VALUES
              (:id, :cedula, :nombre, :apellidos, 'super_admin', 'activo', 0, :fecha, :pw)
        """), {
            "id": eid, "cedula": CEDULA, "nombre": NOMBRE,
            "apellidos": APELLIDO, "fecha": str(date.today()),
            "pw": pwd.hash(PASSWORD)
        })
        db.commit()
        print(f"Admin creado: {CEDULA} / {PASSWORD}")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
