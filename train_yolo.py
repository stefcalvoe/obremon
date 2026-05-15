#!/usr/bin/env python3
"""
train_yolo.py - Entrenamiento de modelo YOLO para detectar personas
Proyecto: Aforador AMSA IA
"""

import os
import yaml
from ultralytics import YOLO
import torch

# Configuración
DATASET_PATH = "./data"
MODEL_NAME = "yolov8m"  # nano, small, medium, large
EPOCHS = 100
BATCH_SIZE = 16
IMG_SIZE = 640
DEVICE = 0 if torch.cuda.is_available() else "cpu"

def create_data_yaml():
    """Crear archivo data.yaml para YOLO"""
    data_yaml = {
        'path': os.path.abspath(DATASET_PATH),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': 1,  # 1 clase: persona
        'names': ['persona']
    }
    
    yaml_path = os.path.join(DATASET_PATH, 'data.yaml')
    with open(yaml_path, 'w') as f:
        yaml.dump(data_yaml, f)
    print(f"✅ data.yaml creado en {yaml_path}")
    return yaml_path

def train_model(yaml_path):
    """Entrenar modelo YOLO"""
    print(f"\n🚀 Iniciando entrenamiento...")
    print(f"   Dispositivo: {DEVICE}")
    print(f"   Modelo: {MODEL_NAME}")
    print(f"   Épocas: {EPOCHS}")
    print(f"   Batch size: {BATCH_SIZE}")
    
    # Cargar modelo preentrenado
    model = YOLO(f'{MODEL_NAME}.pt')
    
    # Entrenar
    results = model.train(
        data=yaml_path,
        epochs=EPOCHS,
        imgsz=IMG_SIZE,
        batch=BATCH_SIZE,
        patience=20,
        device=DEVICE,
        optimizer='SGD',
        lr0=0.001,
        momentum=0.937,
        weight_decay=0.0005,
        augment=True,
        mosaic=1.0,
        mixup=0.1,
        flipud=0.5,
        fliplr=0.5,
        verbose=True,
        save=True,
        project='./models',
        name=f'{MODEL_NAME}_aforador'
    )
    
    print(f"\n✅ Entrenamiento completado!")
    return results

def validate_model():
    """Validar modelo"""
    print("\n🔍 Validando modelo...")
    best_model_path = f'./models/{MODEL_NAME}_aforador/weights/best.pt'
    
    if os.path.exists(best_model_path):
        model = YOLO(best_model_path)
        metrics = model.val()
        print(f"✅ Validación completada!")
        return metrics
    else:
        print(f"❌ Modelo no encontrado en {best_model_path}")
        return None

def export_model():
    """Exportar modelo a formatos"""
    print("\n📦 Exportando modelo...")
    best_model_path = f'./models/{MODEL_NAME}_aforador/weights/best.pt'
    
    if os.path.exists(best_model_path):
        model = YOLO(best_model_path)
        # Exportar a ONNX y TorchScript
        model.export(format='onnx')  # formato='onnx', 'torchscript', 'tflite'
        print(f"✅ Modelo exportado!")
    else:
        print(f"❌ Modelo no encontrado")

if __name__ == "__main__":
    print("="*60)
    print(" ENTRENAMIENTO YOLO - AFORADOR AMSA IA")
    print("="*60)
    
    # Paso 1: Crear data.yaml
    yaml_path = create_data_yaml()
    
    # Paso 2: Entrenar
    results = train_model(yaml_path)
    
    # Paso 3: Validar
    metrics = validate_model()
    
    # Paso 4: Exportar
    export_model()
    
    print("\n" + "="*60)
    print(" ✅ PIPELINE COMPLETADO")
    print("="*60)
