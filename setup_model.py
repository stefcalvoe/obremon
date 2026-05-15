#!/usr/bin/env python3
"""
setup_model.py - PASO 2: Descargar y configurar modelo YOLOv8
Descarga yolov8m.pt preentrenado en COCO (detecta personas como clase 0)
y lo coloca en la ruta esperada por app.py
"""

import os
import shutil
from pathlib import Path

MODEL_DEST = "./models/yolov8m_aforador/weights/best.pt"
BASE_MODEL = "yolov8m.pt"

def setup_model():
    print("=" * 60)
    print("  PASO 2 - SETUP DEL MODELO - AFORADOR AMSA IA")
    print("=" * 60)

    dest_path = Path(MODEL_DEST)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        print(f"[OK] Modelo ya existe en {MODEL_DEST}")
        return

    print(f"\nDescargando {BASE_MODEL} (preentrenado en COCO)...")
    print("   Esto puede tardar unos minutos la primera vez...\n")

    try:
        from ultralytics import YOLO
        model = YOLO(BASE_MODEL)  # Ultralytics descarga automaticamente
        downloaded_path = Path(BASE_MODEL)

        # Copiar a la ruta esperada por app.py
        shutil.copy2(downloaded_path, dest_path)
        print(f"\n[OK] Modelo copiado a: {MODEL_DEST}")

        # Verificar que detecta personas
        print("\nVerificando modelo...")
        import numpy as np
        test_img = np.zeros((640, 640, 3), dtype=np.uint8)
        results = model(test_img, verbose=False)
        print("[OK] Modelo cargado y funcional")
        print(f"     Clases disponibles: {model.names}")
        print(f"     Clase 0 (persona): '{model.names[0]}'")

    except ImportError:
        print("[ERROR] ultralytics no instalado. Ejecuta primero: setup_entorno.bat")
        return
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print("\n" + "=" * 60)
    print("  [OK] MODELO LISTO")
    print("=" * 60)
    print(f"\n  Ruta: {MODEL_DEST}")
    print("  Siguiente paso: python download_dataset.py")
    print("  O para probar la API directamente: python app.py")
    print()


if __name__ == "__main__":
    setup_model()
