#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_counter_fast.py - Contador rapido optimizado
Carga el modelo UNA VEZ y procesa todos los videos
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
DISTANCE_THRESHOLD = 50

class SimplePesonTracker:
    """Tracker simple y rapido."""

    def __init__(self):
        self.tracked = {}
        self.next_id = 1
        self.entrada = 0
        self.salida = 0
        self.max_sim = 0

    def update(self, detections):
        """Actualizar tracking (simplificado para velocidad)."""
        current_cents = []
        for bbox in detections:
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            current_cents.append((cx, cy))

        matched = set()
        for cent in current_cents:
            best_id = None
            best_dist = DISTANCE_THRESHOLD

            for pid, pers in list(self.tracked.items()):
                if pid in matched:
                    continue
                dist = np.sqrt(
                    (cent[0] - pers[0]) ** 2 +
                    (cent[1] - pers[1]) ** 2
                )
                if dist < best_dist:
                    best_dist = dist
                    best_id = pid

            if best_id:
                self.tracked[best_id] = cent
                matched.add(best_id)
            else:
                self.tracked[self.next_id] = cent
                self.entrada += 1
                matched.add(self.next_id)
                self.next_id += 1

        for pid in list(self.tracked.keys()):
            if pid not in matched:
                self.salida += 1
                del self.tracked[pid]

        self.max_sim = max(self.max_sim, len(self.tracked))
        return len(self.tracked)

    def get_result(self):
        return {
            'entrada': self.entrada,
            'salida': self.salida,
            'max_sim': self.max_sim
        }

def process_video(video_path, model):
    """Procesar un video."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracion = total_frames / fps if fps > 0 else 0

    tracker = SimplePesonTracker()
    frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detectar
        results = model(frame, verbose=False)
        detections = []
        for box in results[0].boxes:
            if int(box.cls.item()) == PERSON_CLASS:
                detections.append(box.xyxy[0].tolist())

        # Trackear
        tracker.update(detections)
        frame_num += 1

    cap.release()
    result = tracker.get_result()

    return {
        'video': Path(video_path).name,
        'duracion': duracion,
        'frames': total_frames,
        'personas': result['entrada']
    }

def main():
    videos_dir = Path(r"C:\Users\Stef\Desktop\pruba 2")

    print("="*70)
    print("  AFORADOR INTELIGENTE - MODO RAPIDO")
    print("="*70)

    videos = sorted(videos_dir.glob("Bus080*.mov"))
    print(f"Cargando modelo...", end="", flush=True)

    try:
        model = YOLO(MODEL_PATH)
        print(" OK")
    except:
        print(" [ERROR]")
        return

    print(f"Procesando {len(videos)} videos...\n")

    results = []
    total = 0

    for idx, video in enumerate(videos, 1):
        print(f"[{idx}/{len(videos)}] {video.name}...", end="", flush=True)

        result = process_video(str(video), model)

        if result:
            results.append(result)
            total += result['personas']
            print(f" OK ({result['personas']} personas)")
        else:
            print(f" ERROR")

    print()
    print("="*70)
    print(f"TOTAL PERSONAS EN 24 VIDEOS: {total}")
    print(f"PROMEDIO POR VIDEO: {total / len(results):.1f}")
    print("="*70)

    # Guardar
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_videos': len(results),
        'total_personas': total,
        'promedio': total / len(results) if results else 0,
        'videos': results
    }

    with open("reporte_final.json", 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReporte: reporte_final.json")

    # Mostrar tabla
    print("\nDetalle por video:")
    print("-" * 70)
    for r in results:
        print(f"{r['video']:50s} | {r['personas']:2d} personas")

if __name__ == "__main__":
    main()
