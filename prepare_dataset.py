#!/usr/bin/env python3
"""
prepare_dataset.py - Preparar dataset de videos para entrenamiento YOLO
"""

import os
import shutil
import random
from pathlib import Path

def organize_dataset(source_dir, output_dir, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
    """
    Organizar imágenes en carpetas train/val/test
    
    Estructura esperada:
    source_dir/
    ├── imagen1.jpg
    ├── imagen2.jpg
    ├── label1.txt (YOLO format)
    └── ...
    """
    
    images_dir = os.path.join(output_dir, 'images')
    labels_dir = os.path.join(output_dir, 'labels')
    
    for split in ['train', 'val', 'test']:
        os.makedirs(os.path.join(images_dir, split), exist_ok=True)
        os.makedirs(os.path.join(labels_dir, split), exist_ok=True)
    
    # Listar imágenes
    image_files = [f for f in os.listdir(source_dir) 
                   if f.endswith(('.jpg', '.png', '.jpeg'))]
    
    random.shuffle(image_files)
    
    total = len(image_files)
    train_count = int(total * train_ratio)
    val_count = int(total * val_ratio)
    
    splits = {
        'train': image_files[:train_count],
        'val': image_files[train_count:train_count + val_count],
        'test': image_files[train_count + val_count:]
    }
    
    # Copiar archivos
    for split, files in splits.items():
        for img_file in files:
            src_img = os.path.join(source_dir, img_file)
            dst_img = os.path.join(images_dir, split, img_file)
            
            label_file = img_file.rsplit('.', 1)[0] + '.txt'
            src_label = os.path.join(source_dir, label_file)
            dst_label = os.path.join(labels_dir, split, label_file)
            
            shutil.copy2(src_img, dst_img)
            if os.path.exists(src_label):
                shutil.copy2(src_label, dst_label)
        
        print(f"✅ {split.upper()}: {len(files)} imágenes")
    
    print(f"\n✅ Dataset organizado en: {output_dir}")
    return output_dir

def extract_frames_from_video(video_path, output_dir, frame_interval=5):
    """
    Extraer frames de video para anotar
    
    frame_interval: cada N frames extraer 1
    """
    import cv2
    
    print(f"\n📹 Extrayendo frames de: {video_path}")
    
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    saved_count = 0
    
    os.makedirs(output_dir, exist_ok=True)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            frame_path = os.path.join(output_dir, f"frame_{saved_count:06d}.jpg")
            cv2.imwrite(frame_path, frame)
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"✅ {saved_count} frames extraídos")
    return output_dir

def validate_yolo_format(labels_dir):
    """
    Validar que labels estén en formato YOLO
    
    Formato YOLO:
    <class_id> <x_center> <y_center> <width> <height>
    (todos valores normalizados 0-1)
    """
    
    print("\n✓ Validando formato YOLO...")
    
    valid = 0
    invalid = 0
    
    for label_file in Path(labels_dir).rglob("*.txt"):
        with open(label_file) as f:
            lines = f.readlines()
            for line in lines:
                parts = line.strip().split()
                if len(parts) != 5:
                    invalid += 1
                    continue
                
                try:
                    class_id = int(parts[0])
                    coords = [float(x) for x in parts[1:]]
                    
                    if all(0 <= c <= 1 for c in coords):
                        valid += 1
                    else:
                        invalid += 1
                except:
                    invalid += 1
    
    print(f"✅ Válidos: {valid} | ❌ Inválidos: {invalid}")

if __name__ == "__main__":
    print("="*60)
    print(" PREPARAR DATASET - AFORADOR AMSA IA")
    print("="*60)
    
    # Paso 1: Extraer frames de video (si tienes videos)
    # extract_frames_from_video("ruta40_video.mp4", "./raw_frames", frame_interval=10)
    
    # Paso 2: Organizar en train/val/test
    source_dir = "./raw_frames"  # Cambiar a tu directorio de imágenes
    output_dir = "./data"
    
    if os.path.exists(source_dir):
        organize_dataset(source_dir, output_dir)
    else:
        print(f"⚠️ Directorio {source_dir} no encontrado")
        print("   Crea una carpeta 'raw_frames' con tus imágenes anotadas")
    
    # Paso 3: Validar
    labels_dir = os.path.join(output_dir, 'labels')
    if os.path.exists(labels_dir):
        validate_yolo_format(labels_dir)
    
    print("\n" + "="*60)
