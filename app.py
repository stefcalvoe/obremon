#!/usr/bin/env python3
"""
app.py - API FastAPI para Aforador AMSA IA
Endpoints para predicción de conteo de personas
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import cv2
import numpy as np
import io
import os
import tempfile
from pathlib import Path

# Configuración
MODEL_PATH = "./models/yolov8m_aforador/weights/best.pt"
FALLBACK_MODEL = "yolov8m.pt"   # modelo COCO base si no hay fine-tuned
PERSON_CLASS_ID = 0             # clase 0 = persona en COCO
APP_TITLE = "Aforador AMSA IA API"

# Inicializar FastAPI
app = FastAPI(
    title=APP_TITLE,
    description="API para conteo automático de pasajeros con IA",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cargar modelo (fine-tuned si existe, sino modelo COCO base)
model = None
if os.path.exists(MODEL_PATH):
    try:
        model = YOLO(MODEL_PATH)
        print(f"✅ Modelo fine-tuned cargado: {MODEL_PATH}")
    except Exception as e:
        print(f"❌ Error cargando modelo fine-tuned: {e}")

if model is None:
    try:
        model = YOLO(FALLBACK_MODEL)
        print(f"⚠️  Usando modelo base COCO: {FALLBACK_MODEL}")
        print("   Ejecuta train_yolo.py para obtener el modelo fine-tuned")
    except Exception as e:
        print(f"❌ Error cargando modelo base: {e}")

# ═══════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Info del API"""
    return {
        "app": APP_TITLE,
        "version": "1.0.0",
        "status": "online" if model else "model_not_loaded",
        "endpoints": {
            "predict_frame": "POST /predict",
            "predict_video": "POST /predict_video",
            "health": "GET /health"
        }
    }

@app.get("/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Predecir conteo en un frame/imagen"""
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    
    try:
        # Leer imagen
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Imagen inválida")
        
        # Predicción — filtrar solo personas (clase 0)
        results = model(img)
        all_boxes = results[0].boxes
        detections = [b for b in all_boxes if int(b.cls.item()) == PERSON_CLASS_ID]

        return {
            "file_name": file.filename,
            "total_personas": len(detections),
            "detections": [
                {
                    "class": int(box.cls.item()),
                    "confidence": float(box.conf.item()),
                    "bbox": box.xyxy.tolist()[0]
                }
                for box in detections
            ],
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/predict_video")
async def predict_video(file: UploadFile = File(...)):
    """Predecir conteo en video completo"""
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    
    try:
        # Guardar video temporalmente (compatible con Windows)
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp:
            tmp.write(contents)
            temp_path = tmp.name
        
        # Procesar video
        cap = cv2.VideoCapture(temp_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        person_counts = []
        frame_detections = []
        
        frame_id = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Predicción por frame — filtrar solo personas
            results = model(frame)
            detections = [b for b in results[0].boxes if int(b.cls.item()) == PERSON_CLASS_ID]
            count = len(detections)
            person_counts.append(count)
            
            frame_detections.append({
                "frame": frame_id,
                "count": count,
                "confidence": float(detections[0].conf.item()) if len(detections) > 0 else 0
            })
            
            frame_id += 1
        
        cap.release()
        os.remove(temp_path)
        
        avg_count = np.mean(person_counts) if person_counts else 0
        total_count = sum(person_counts)
        
        return {
            "file_name": file.filename,
            "total_frames": frame_id,
            "total_personas_sum": total_count,
            "promedio_personas_frame": float(avg_count),
            "frame_detections": frame_detections[:10],  # Primeros 10 frames
            "status": "success"
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/batch_predict")
async def batch_predict(files: list = File(...)):
    """Predicción en lote"""
    if model is None:
        raise HTTPException(status_code=500, detail="Modelo no cargado")
    
    results = []
    for file in files:
        try:
            contents = await file.read()
            nparr = np.frombuffer(contents, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            pred = model(img)
            count = sum(1 for b in pred[0].boxes if int(b.cls.item()) == PERSON_CLASS_ID)
            
            results.append({
                "file": file.filename,
                "count": count,
                "status": "ok"
            })
        except Exception as e:
            results.append({
                "file": file.filename,
                "error": str(e),
                "status": "error"
            })
    
    return {
        "total_files": len(files),
        "results": results
    }

# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print(" 🚀 AFORADOR AMSA IA - API SERVER")
    print("="*60)
    print(f"📍 http://localhost:8000")
    print(f"📚 Docs: http://localhost:8000/docs")
    print("="*60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
