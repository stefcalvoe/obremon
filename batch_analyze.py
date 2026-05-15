#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
batch_analyze.py - Analizar multiples videos en lote y generar reporte consolidado
"""

import requests
import json
import sys
import os
import subprocess
import time
from pathlib import Path
from datetime import datetime
import io

# Fix encoding para Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000"
VIDEOS_DIR = r"C:\Users\Stef\Desktop\pruba 2"

def ensure_api_running():
    """Asegurar que el API este corriendo."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            r = requests.get(f"{API_URL}/health", timeout=2)
            if r.status_code == 200:
                print("[OK] API disponible")
                return True
        except:
            pass

        if attempt < max_retries - 1:
            print("[...] Iniciando API...")
            subprocess.Popen(
                ["./venv/Scripts/python", "app.py"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(5)

    return False

def analyze_video(video_path, timeout=120):
    """Enviar video al API para analisis."""
    try:
        with open(video_path, 'rb') as f:
            r = requests.post(
                f"{API_URL}/predict_video",
                files={'file': f},
                timeout=timeout
            )

        if r.status_code == 200:
            return r.json()
        return None
    except:
        return None

def process_batch(videos_dir):
    """Procesar todos los videos en un directorio."""
    if not ensure_api_running():
        print("[ERROR] No se puede conectar al API")
        return

    videos = sorted(Path(videos_dir).glob("Bus080*.mov"))
    print(f"Encontrados {len(videos)} videos\n")

    results = []
    total_personas = 0

    for idx, video_path in enumerate(videos, 1):
        filename = video_path.name
        print(f"[{idx}/{len(videos)}] {filename}...", end=" ", flush=True)

        result = analyze_video(str(video_path))

        if result and result.get('status') == 'success':
            count = result.get('total_personas_sum', 0)
            total_personas += count
            results.append({
                'video': filename,
                'frames': result.get('total_frames'),
                'personas': count,
                'promedio': result.get('promedio_personas_frame')
            })
            print(f"[OK] {count} personas")
        else:
            print(f"[ERROR]")
            results.append({
                'video': filename,
                'personas': 0,
                'error': True
            })

    # Generar reporte
    print("\n" + "="*70)
    print("  REPORTE CONSOLIDADO - 24 VIDEOS BUS080")
    print("="*70)
    print()

    for r in results:
        status = "[OK]" if not r.get('error') else "[ERR]"
        print(f"{status} {r['video']:45s} | {r['personas']:3d} personas")

    print()
    print("="*70)
    print(f"TOTAL PERSONAS DETECTADAS EN {len(results)} VIDEOS: {total_personas}")
    print("="*70)

    # Guardar reporte JSON
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_videos': len(results),
        'total_personas': total_personas,
        'videos': results
    }

    with open("reporte_batch.json", 'w') as f:
        json.dump(report, f, indent=2)

    print("\n[OK] Reporte guardado en: reporte_batch.json")

if __name__ == "__main__":
    process_batch(VIDEOS_DIR)
