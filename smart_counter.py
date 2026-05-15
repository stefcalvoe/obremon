#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_counter.py - Contador inteligente de personas con tracking
Usa centroide tracking para contar personas únicas (no duplicadas por frame)
Detecta entrada/salida basado en movimiento
"""

import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import json
from datetime import datetime
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MODEL_PATH = "./models/yolov8m_aforador/weights/best.pt"
PERSON_CLASS = 0
DISTANCE_THRESHOLD = 50  # Distancia maxima para considerar la misma persona

class PersonTracker:
    """Tracker de personas usando centroides."""

    def __init__(self):
        self.tracked_persons = {}  # {id: {centroid, frames_visto, entrada_frame, salida_frame}}
        self.next_id = 1
        self.personas_entraron = 0
        self.personas_salieron = 0
        self.max_personas_simultaneas = 0
        self.frame_history = []

    def update(self, detections, frame_num, frame_shape):
        """
        Actualizar tracking con nuevas detecciones.
        detections: lista de [x1, y1, x2, y2, conf] (bbox en pixels)
        """
        h, w = frame_shape[:2]

        # Calcular centroides de detecciones actuales
        current_centroids = []
        for bbox in detections:
            x1, y1, x2, y2 = bbox[:4]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            current_centroids.append((cx, cy))

        # Asociar detecciones con tracks existentes
        matched_ids = set()
        for cent in current_centroids:
            best_id = None
            best_dist = DISTANCE_THRESHOLD

            for pid, person in self.tracked_persons.items():
                if pid in matched_ids:
                    continue

                dist = np.sqrt(
                    (cent[0] - person['centroid'][0]) ** 2 +
                    (cent[1] - person['centroid'][1]) ** 2
                )

                if dist < best_dist:
                    best_dist = dist
                    best_id = pid

            if best_id is not None:
                # Persona existente
                self.tracked_persons[best_id]['centroid'] = cent
                self.tracked_persons[best_id]['frames_visto'] += 1
                matched_ids.add(best_id)
            else:
                # Nueva persona detectada
                new_id = self.next_id
                self.next_id += 1
                self.tracked_persons[new_id] = {
                    'centroid': cent,
                    'frames_visto': 1,
                    'entrada_frame': frame_num,
                    'salida_frame': None
                }
                self.personas_entraron += 1
                matched_ids.add(new_id)

        # Personas que desaparecieron
        for pid in list(self.tracked_persons.keys()):
            if pid not in matched_ids:
                self.tracked_persons[pid]['salida_frame'] = frame_num
                self.personas_salieron += 1
                del self.tracked_persons[pid]

        # Contar personas actuales en frame
        personas_actuales = len(self.tracked_persons)
        self.max_personas_simultaneas = max(self.max_personas_simultaneas, personas_actuales)

        return personas_actuales

    def get_summary(self):
        """Resumen del tracking."""
        return {
            'personas_entraron': self.personas_entraron,
            'personas_salieron': self.personas_salieron,
            'max_simultaneas': self.max_personas_simultaneas,
            'personas_actualmente': len(self.tracked_persons)
        }

def analyze_video_smart(video_path):
    """Analizar video con tracking inteligente."""
    print(f"\nAnalizando: {Path(video_path).name}")

    # Cargar modelo
    try:
        model = YOLO(MODEL_PATH)
    except:
        print("[ERROR] Modelo no encontrado")
        return None

    # Abrir video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("[ERROR] No se pudo abrir video")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracion_segundos = total_frames / fps if fps > 0 else 0

    print(f"   Duracion: {duracion_segundos:.1f}s | {total_frames} frames | {fps:.1f} fps")

    tracker = PersonTracker()
    frame_num = 0
    frame_detections = []

    print("   Procesando...", end="", flush=True)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar personas
        results = model(frame, verbose=False)
        detections = []

        for box in results[0].boxes:
            if int(box.cls.item()) == PERSON_CLASS:
                detections.append(box.xyxy[0].tolist())

        # Actualizar tracking
        personas_frame = tracker.update(detections, frame_num, frame.shape)

        frame_detections.append({
            'frame': frame_num,
            'detecciones_raw': len(detections),
            'personas_tracking': personas_frame,
            'personas_totales_vistas': tracker.personas_entraron
        })

        frame_num += 1
        if frame_num % 50 == 0:
            print(".", end="", flush=True)

    cap.release()
    print(" OK")

    # Resultado final
    summary = tracker.get_summary()

    return {
        'video': Path(video_path).name,
        'duracion_segundos': duracion_segundos,
        'total_frames': total_frames,
        'fps': fps,
        'personas_entraron': summary['personas_entraron'],
        'personas_salieron': summary['personas_salieron'],
        'max_simultaneas': summary['max_simultaneas'],
        'frame_detections': frame_detections[:20]  # Primeros 20 frames
    }

def batch_analyze(videos_dir):
    """Analizar todos los videos en un directorio."""
    videos = sorted(Path(videos_dir).glob("Bus080*.mov"))

    print("="*70)
    print("  AFORADOR INTELIGENTE - ANALISIS CON TRACKING")
    print("="*70)
    print(f"Analizando {len(videos)} videos...\n")

    results = []
    total_personas_red = 0

    for idx, video_path in enumerate(videos, 1):
        result = analyze_video_smart(str(video_path))

        if result:
            results.append(result)
            total_personas_red += result['personas_entraron']
            print(f"   [{idx}/{len(videos)}] {result['personas_entraron']} personas")
        else:
            print(f"   [{idx}/{len(videos)}] ERROR")

    # Reporte final
    print("\n" + "="*70)
    print("  REPORTE FINAL - 24 VIDEOS")
    print("="*70)
    print()

    for r in results:
        print(f"{r['video']:50s} | {r['personas_entraron']:2d} personas")

    print()
    print("="*70)
    print(f"TOTAL PERSONAS (REAL) EN 24 VIDEOS: {total_personas_red}")
    print(f"PROMEDIO POR VIDEO: {total_personas_red / len(results):.1f}")
    print("="*70)

    # Guardar reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_videos': len(results),
        'total_personas_real': total_personas_red,
        'promedio_por_video': total_personas_red / len(results) if results else 0,
        'videos': results
    }

    with open("reporte_smart.json", 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReporte guardado: reporte_smart.json")
    print()

    return total_personas_red, results

if __name__ == "__main__":
    videos_dir = r"C:\Users\Stef\Desktop\pruba 2"

    if not Path(videos_dir).exists():
        print(f"[ERROR] Directorio no encontrado: {videos_dir}")
        sys.exit(1)

    total, results = batch_analyze(videos_dir)
