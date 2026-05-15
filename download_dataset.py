#!/usr/bin/env python3
"""
download_dataset.py - PASO 3: Descargar dataset de personas para entrenamiento
Descarga COCO128 (incluido en ultralytics) y filtra solo imagenes con personas.
Resultado: ./data/ listo para train_yolo.py
"""

import os
import shutil
import yaml
import random
from pathlib import Path

OUTPUT_DIR = "./data"
TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
# test usa el resto (0.15)

def download_coco128():
    """Descarga COCO128 usando ultralytics."""
    print("Descargando COCO128 (dataset de muestra de COCO)...")
    from ultralytics.utils import DATASETS_DIR
    from ultralytics import settings
    import ultralytics.data.utils as du

    # Forzar descarga de coco128
    du.check_det_dataset("coco128.yaml")
    coco128_path = Path(settings["datasets_dir"]) / "coco128"
    print(f"[OK] Dataset en: {coco128_path}")
    return coco128_path


def filter_person_images(coco128_path, output_dir):
    """
    Copia al output_dir solo las imagenes que tienen anotaciones de persona (clase 0).
    Reescribe los labels dejando solo las anotaciones de clase 0, renumerada a 0.
    """
    raw_dir = Path(output_dir) / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    images_src = coco128_path / "images" / "train2017"
    labels_src = coco128_path / "labels" / "train2017"

    if not images_src.exists():
        print(f"[ERROR] No se encontraron imagenes en {images_src}")
        return 0

    copied = 0
    for label_file in labels_src.glob("*.txt"):
        lines = label_file.read_text().strip().splitlines()
        person_lines = [l for l in lines if l.startswith("0 ")]
        if not person_lines:
            continue

        img_stem = label_file.stem
        img_file = None
        for ext in (".jpg", ".jpeg", ".png"):
            candidate = images_src / (img_stem + ext)
            if candidate.exists():
                img_file = candidate
                break
        if img_file is None:
            continue

        shutil.copy2(img_file, raw_dir / img_file.name)
        (raw_dir / label_file.name).write_text("\n".join(person_lines))
        copied += 1

    print(f"[OK] {copied} imagenes con personas copiadas a {raw_dir}")
    return copied


def split_dataset(raw_dir, output_dir):
    """Divide raw/ en train/val/test manteniendo pares imagen+label."""
    images_out = Path(output_dir) / "images"
    labels_out = Path(output_dir) / "labels"

    for split in ("train", "val", "test"):
        (images_out / split).mkdir(parents=True, exist_ok=True)
        (labels_out / split).mkdir(parents=True, exist_ok=True)

    image_files = [
        f for f in Path(raw_dir).iterdir()
        if f.suffix.lower() in (".jpg", ".jpeg", ".png")
    ]
    random.shuffle(image_files)

    n = len(image_files)
    n_train = int(n * TRAIN_RATIO)
    n_val   = int(n * VAL_RATIO)

    splits = {
        "train": image_files[:n_train],
        "val":   image_files[n_train:n_train + n_val],
        "test":  image_files[n_train + n_val:],
    }

    for split, files in splits.items():
        for img in files:
            shutil.copy2(img, images_out / split / img.name)
            label = Path(raw_dir) / (img.stem + ".txt")
            if label.exists():
                shutil.copy2(label, labels_out / split / label.name)
        print(f"  {split.upper():5s}: {len(files)} imagenes")

    return n


def create_data_yaml(output_dir):
    """Crea data.yaml listo para train_yolo.py."""
    data = {
        "path": str(Path(output_dir).resolve()),
        "train": "images/train",
        "val":   "images/val",
        "test":  "images/test",
        "nc":    1,
        "names": ["persona"],
    }
    yaml_path = Path(output_dir) / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
    print(f"[OK] data.yaml creado en {yaml_path}")
    return yaml_path


if __name__ == "__main__":
    print("=" * 60)
    print("  PASO 3 - DATASET - AFORADOR AMSA IA")
    print("=" * 60)

    try:
        coco128_path = download_coco128()
    except Exception as e:
        print(f"[ERROR] No se pudo descargar COCO128: {e}")
        print("Asegurate de haber ejecutado setup_entorno.bat primero.")
        raise SystemExit(1)

    raw_dir = Path(OUTPUT_DIR) / "raw"
    total = filter_person_images(coco128_path, OUTPUT_DIR)

    if total == 0:
        print("[ERROR] No se encontraron imagenes con personas.")
        raise SystemExit(1)

    print(f"\nDividiendo {total} imagenes en train/val/test...")
    split_dataset(raw_dir, OUTPUT_DIR)

    yaml_path = create_data_yaml(OUTPUT_DIR)

    # Limpiar carpeta raw temporal
    shutil.rmtree(raw_dir, ignore_errors=True)

    print()
    print("=" * 60)
    print("  [OK] DATASET LISTO")
    print("=" * 60)
    print(f"\n  Estructura en: {OUTPUT_DIR}/")
    print("  ├── images/train/  val/  test/")
    print("  ├── labels/train/  val/  test/")
    print("  └── data.yaml")
    print()
    print("  Siguiente paso: python train_yolo.py")
    print()
