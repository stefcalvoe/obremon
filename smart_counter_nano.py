#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
smart_counter_nano.py - Analisis rapido con YOLOv8 NANO
5-10 minutos para 24 videos en lugar de horas
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

# Usar modelo NANO (3x mas rapido que MEDIUM)
MODEL_NAME = "yolov8n.pt"  # NANO en lugar de medium
PERSON_CLASS = 0
SKIP_FRAMES = 5  # Procesar cada 5to frame para acelerar mas

class SimpleTracker:
    def __init__(self):
        self.tracked = {}
        self.next_id = 1
        self.entrada = 0
        self.salida = 0

    def update(self, detections):
        current = []
        for bbox in detections:
            cx, cy = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2
            current.append((cx, cy))

        matched = set()
        for cent in current:
            best_id = None
            best_dist = 50

            for pid, pos in list(self.tracked.items()):
                if pid in matched:
                    continue
                dist = np.sqrt((cent[0] - pos[0]) ** 2 + (cent[1] - pos[1]) ** 2)
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

        return len(self.tracked)

def analyze_video(video_path, model):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duracion = total_frames / fps if fps > 0 else 0

    tracker = SimpleTracker()
    frame_num = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Saltar frames para acelerar
        if frame_num % SKIP_FRAMES == 0:
            results = model(frame, verbose=False, conf=0.5)
            detections = []
            for box in results[0].boxes:
                if int(box.cls.item()) == PERSON_CLASS:
                    detections.append(box.xyxy[0].tolist())
            tracker.update(detections)

        frame_num += 1

    cap.release()

    return {
        'video': Path(video_path).name,
        'duracion': f"{duracion:.1f}s",
        'frames': total_frames,
        'personas': tracker.entrada
    }

def main():
    videos_dir = Path(r"C:\Users\Stef\Desktop\pruba 2")
    videos = sorted(videos_dir.glob("Bus080*.mov"))

    print("="*70)
    print("  AFORADOR INTELIGENTE - MODO RAPIDO (NANO)")
    print("="*70)
    print(f"\nCargando modelo {MODEL_NAME}...", end="", flush=True)

    try:
        model = YOLO(MODEL_NAME)
        print(" OK")
    except Exception as e:
        print(f" ERROR: {e}")
        return

    print(f"Procesando {len(videos)} videos...")
    print(f"(Procesando cada {SKIP_FRAMES}to frame para acelerar)\n")

    results = []
    total = 0

    for idx, video in enumerate(videos, 1):
        print(f"[{idx:2d}/{len(videos)}] {video.name:50s}...", end="", flush=True)

        result = analyze_video(str(video), model)

        if result:
            results.append(result)
            total += result['personas']
            print(f" OK ({result['personas']:2d} personas)")
        else:
            print(f" ERROR")

    print()
    print("="*70)
    print(f"TOTAL PERSONAS DETECTADAS: {total}")
    print(f"PROMEDIO POR VIDEO: {total / len(results):.1f}")
    print("="*70)

    # Guardar reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'metodo': f'YOLOv8 NANO, skip={SKIP_FRAMES} frames',
        'total_videos': len(results),
        'total_personas': total,
        'promedio': total / len(results) if results else 0,
        'videos': results
    }

    with open("reporte_nano.json", 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReporte: reporte_nano.json\n")

    # Tabla
    print("Video                                          | Personas | Duracion")
    print("-" * 70)
    for r in results:
        print(f"{r['video']:45s} | {r['personas']:8d} | {r['duracion']:8s}")

    return total, results

if __name__ == "__main__":
    main()
