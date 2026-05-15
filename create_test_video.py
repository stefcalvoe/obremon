#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
create_test_video.py - Crear video de prueba con imágenes del dataset
Genera un video MP4 usando las imágenes que ya tenemos
"""

import cv2
import os
import sys
from pathlib import Path

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_test_video():
    output_file = "test_video.mp4"
    images_dir = Path("data/images/train")

    if not images_dir.exists():
        print(f"❌ Directorio no encontrado: {images_dir}")
        return False

    # Obtener imágenes
    image_files = sorted([f for f in images_dir.glob("*.jpg")])[:10]  # Primeras 10

    if not image_files:
        print(f"❌ No hay imágenes en {images_dir}")
        return False

    print(f"📸 Usando {len(image_files)} imágenes para crear video...")

    # Leer primera imagen para obtener dimensiones
    first_img = cv2.imread(str(image_files[0]))
    height, width = first_img.shape[:2]

    # Crear video writer (30 fps, 3 segundos de video)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 10.0, (width, height))

    # Escribir cada imagen 3 veces (para duración)
    for img_path in image_files:
        img = cv2.imread(str(img_path))
        for _ in range(3):  # Repetir cada imagen 3 frames
            out.write(img)

    out.release()

    size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"✅ Video creado: {output_file} ({size_mb:.1f} MB)")
    print(f"   Duración: ~3 segundos")
    print(f"   Frames: {len(image_files) * 3}")
    print(f"   Resolución: {width}x{height}")
    return True

if __name__ == "__main__":
    create_test_video()
