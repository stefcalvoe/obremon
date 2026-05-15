#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_analysis.py - Demo rapido de analisis sin necesidad del API en background
Simula resultados y muestra como genera reportes
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
import matplotlib.pyplot as plt

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

OUTPUT_DIR = "./reportes/test_video"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# Simular resultados del API (como si los hubiera enviado)
simulated_results = {
    "file_name": "test_video.mp4",
    "total_frames": 30,
    "total_personas_sum": 50,
    "promedio_personas_frame": 1.67,
    "frame_detections": [
        {"frame": i, "count": (i % 5) + 1, "confidence": 0.85 + (i % 10) * 0.01}
        for i in range(30)
    ],
    "status": "success"
}

def save_json_report():
    report_path = Path(OUTPUT_DIR) / "reporte.json"
    report = {
        "timestamp": datetime.now().isoformat(),
        "video_file": "test_video.mp4",
        "resultados": simulated_results
    }
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✅ Reporte JSON: {report_path}")

def save_csv_report():
    csv_path = Path(OUTPUT_DIR) / "frame_detections.csv"
    with open(csv_path, 'w') as f:
        f.write("frame,personas_detectadas,confianza_promedio\n")
        for det in simulated_results['frame_detections']:
            f.write(f"{det['frame']},{det['count']},{det['confidence']:.4f}\n")
    print(f"✅ CSV de frames: {csv_path}")

def generate_chart():
    detections = simulated_results['frame_detections']
    frames = [d['frame'] for d in detections]
    counts = [d['count'] for d in detections]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

    # Gráfico 1: Línea
    ax1.plot(frames, counts, linewidth=2.5, color='#2ea043', marker='o', markersize=5)
    ax1.fill_between(frames, counts, alpha=0.3, color='#2ea043')
    ax1.set_xlabel('Frame', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Personas detectadas', fontsize=11, fontweight='bold')
    ax1.set_title('Conteo de Personas por Frame', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('#f8f9fa')

    # Gráfico 2: Histograma
    ax2.hist(counts, bins=5, color='#1a73e8', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Numero de Personas', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Frecuencia (frames)', fontsize=11, fontweight='bold')
    ax2.set_title('Distribucion de Conteos', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    ax2.set_facecolor('#f8f9fa')

    chart_path = Path(OUTPUT_DIR) / "charts.png"
    plt.tight_layout()
    plt.savefig(chart_path, dpi=100, bbox_inches='tight')
    plt.close()

    print(f"✅ Graficos: {chart_path}")

def print_summary():
    r = simulated_results
    print("\n" + "="*60)
    print("  REPORTE DE ANALISIS - AFORADOR AMSA IA")
    print("="*60)
    print(f"\nVideo: {r['file_name']}")
    print(f"Frames procesados: {r['total_frames']}")
    print(f"Total personas (suma): {r['total_personas_sum']}")
    print(f"Promedio por frame: {r['promedio_personas_frame']:.2f}")

    detections = r['frame_detections']
    min_personas = min(d['count'] for d in detections)
    max_personas = max(d['count'] for d in detections)
    print(f"Minimo en un frame: {min_personas}")
    print(f"Maximo en un frame: {max_personas}")
    print(f"\nReportes guardados en: {OUTPUT_DIR}/")

if __name__ == "__main__":
    print("="*60)
    print("  DEMO: ANALISIS DE VIDEO - AFORADOR AMSA IA")
    print("="*60)

    print_summary()
    save_json_report()
    save_csv_report()
    generate_chart()

    print("\n" + "="*60)
    print("  EXITOSO")
    print("="*60)
