#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
analyze_video.py - Procesar videos con el API y generar reportes detallados
Uso: python analyze_video.py video.mp4
"""

import requests
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import cv2
import numpy as np

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:8000"
OUTPUT_DIR = "./reportes"

class VideoAnalyzer:
    def __init__(self, video_path, api_url=API_URL):
        self.video_path = video_path
        self.api_url = api_url
        self.results = None
        self.output_dir = Path(OUTPUT_DIR) / Path(video_path).stem
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_api(self):
        """Verificar que el API esté disponible."""
        try:
            r = requests.get(f"{self.api_url}/health", timeout=2)
            if r.status_code == 200:
                print("✅ API disponible en", self.api_url)
                return True
        except:
            pass
        print("❌ API no disponible en", self.api_url)
        return False

    def validate_video(self):
        """Validar que el archivo sea un video válido."""
        if not os.path.exists(self.video_path):
            print(f"❌ Archivo no encontrado: {self.video_path}")
            return False

        try:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                print(f"❌ No se pudo abrir el video: {self.video_path}")
                return False

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()

            if frame_count == 0:
                print("❌ El video no tiene frames")
                return False

            print(f"✅ Video válido: {frame_count} frames | {fps:.1f} fps | {width}x{height}")
            return True
        except Exception as e:
            print(f"❌ Error validando video: {e}")
            return False

    def predict(self):
        """Enviar video al API para predicción."""
        print(f"\n🚀 Analizando video (esto puede tardar)...")
        print(f"   Archivo: {self.video_path}")

        try:
            with open(self.video_path, 'rb') as f:
                files = {'file': f}
                r = requests.post(
                    f"{self.api_url}/predict_video",
                    files=files,
                    timeout=300
                )

            if r.status_code != 200:
                print(f"❌ Error en API: {r.status_code}")
                print(r.text)
                return False

            self.results = r.json()
            print(f"✅ Análisis completado")
            return True

        except requests.exceptions.Timeout:
            print("❌ Timeout: video muy largo o API lento")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def print_summary(self):
        """Imprimir resumen en consola."""
        if not self.results:
            return

        r = self.results
        print("\n" + "="*60)
        print(f" 📊 REPORTE DE ANÁLISIS")
        print("="*60)
        print(f"\nVideo: {self.video_path}")
        print(f"Frames procesados: {r['total_frames']}")
        print(f"Total personas (suma): {r['total_personas_sum']}")
        print(f"Promedio por frame: {r['promedio_personas_frame']:.2f}")

        if r['frame_detections']:
            detections = r['frame_detections']
            min_personas = min(d['count'] for d in detections)
            max_personas = max(d['count'] for d in detections)
            print(f"Mínimo en un frame: {min_personas}")
            print(f"Máximo en un frame: {max_personas}")

    def save_json_report(self):
        """Guardar reporte en JSON."""
        if not self.results:
            return

        report_path = self.output_dir / "reporte.json"
        report = {
            "timestamp": datetime.now().isoformat(),
            "video_file": self.video_path,
            "api_url": self.api_url,
            "resultados": self.results
        }

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Reporte JSON: {report_path}")

    def save_csv_report(self):
        """Guardar detección por frame en CSV."""
        if not self.results or not self.results.get('frame_detections'):
            return

        csv_path = self.output_dir / "frame_detections.csv"

        with open(csv_path, 'w') as f:
            f.write("frame,personas_detectadas,confianza_promedio\n")
            for det in self.results['frame_detections']:
                f.write(f"{det['frame']},{det['count']},{det['confidence']:.4f}\n")

        print(f"✅ CSV de frames: {csv_path}")

    def generate_chart(self):
        """Generar gráfico de conteo por frame."""
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            print("⚠️  matplotlib no instalado (saltar gráfico)")
            return

        if not self.results or not self.results.get('frame_detections'):
            return

        detections = self.results['frame_detections']
        frames = [d['frame'] for d in detections]
        counts = [d['count'] for d in detections]

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(frames, counts, linewidth=2, color='#2ea043', marker='o', markersize=4)
        ax.fill_between(frames, counts, alpha=0.3, color='#2ea043')

        ax.set_xlabel('Frame', fontsize=11)
        ax.set_ylabel('Personas detectadas', fontsize=11)
        ax.set_title(f'Conteo de Personas por Frame - {Path(self.video_path).name}', fontsize=13, fontweight='bold')
        ax.grid(True, alpha=0.3)

        chart_path = self.output_dir / "chart_conteo.png"
        plt.tight_layout()
        plt.savefig(chart_path, dpi=100, bbox_inches='tight')
        plt.close()

        print(f"✅ Gráfico: {chart_path}")

    def generate_annotated_video(self):
        """Generar video anotado con bounding boxes."""
        print("\n📹 Generando video anotado (esto toma más tiempo)...")

        try:
            cap = cv2.VideoCapture(self.video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            output_path = self.output_dir / f"output_annotated.mp4"
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))

            frame_idx = 0
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Dibujar información del frame
                count = len(self.results['frame_detections']) > frame_idx and \
                       self.results['frame_detections'][frame_idx]['count'] or 0

                cv2.putText(frame, f"Frame: {frame_idx}", (10, 30),
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Personas: {count}", (10, 70),
                          cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

                out.write(frame)
                frame_idx += 1

                if frame_idx % 30 == 0:
                    print(f"   Procesados {frame_idx} frames...", end='\r')

            cap.release()
            out.release()

            print(f"\n✅ Video anotado: {output_path}")

        except Exception as e:
            print(f"⚠️  No se pudo generar video anotado: {e}")

    def run(self):
        """Ejecutar análisis completo."""
        print("="*60)
        print(" 🎥 AFORADOR - ANÁLISIS DE VIDEO")
        print("="*60)

        if not self.check_api():
            print("\n💡 Inicia el API con: python app.py")
            return False

        if not self.validate_video():
            return False

        if not self.predict():
            return False

        self.print_summary()
        self.save_json_report()
        self.save_csv_report()
        self.generate_chart()
        self.generate_annotated_video()

        print("\n" + "="*60)
        print(f" ✅ Reportes guardados en: {self.output_dir}")
        print("="*60)
        return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_video.py <video.mp4>")
        print("\nEjemplos:")
        print("  python analyze_video.py bus.mp4")
        print("  python analyze_video.py /ruta/a/video.mp4")
        sys.exit(1)

    video_file = sys.argv[1]
    analyzer = VideoAnalyzer(video_file)
    success = analyzer.run()
    sys.exit(0 if success else 1)
