import cv2
import json
import matplotlib.pyplot as plt
from ultralytics import YOLO

# -----------------------------
# Configuración
# -----------------------------
model = YOLO("yolov8n.pt")          # YOLO-lite
video_path = "evidence/video.mp4"           # <-- pon aquí tu video

cap = cv2.VideoCapture(video_path)

# -----------------------------
# Variables
# -----------------------------
detecciones_frames = []
conteo_personas = []
frame_id = 0

# -----------------------------
# Procesar el video
# -----------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # -------- YOLO --------
    results = model(frame)

    personas_en_frame = 0
    objetos_frame = []

    if results[0].boxes is not None:
        for r in results[0].boxes:
            clase = model.names[int(r.cls)]
            score = float(r.conf)
            bbox = r.xyxy.tolist()[0]

            objetos_frame.append({
                "clase": clase,
                "score": score,
                "bbox": bbox
            })

            if clase == "person":
                personas_en_frame += 1

    # Guardar resultados de este frame
    detecciones_frames.append({
        "frame": frame_id,
        "personas": personas_en_frame,
        "objetos": objetos_frame
    })

    conteo_personas.append(personas_en_frame)
    frame_id += 1

# -----------------------------
# Liberar video
# -----------------------------
cap.release()

# -----------------------------
# Guardar JSON
# -----------------------------
with open("detecciones_video.json", "w") as f:
    json.dump(detecciones_frames, f, indent=4)

print("✅ Archivo detecciones_video.json generado")

plt.figure()
plt.plot(conteo_personas)
plt.xlabel("Frame")
plt.ylabel("Personas detectadas")
plt.title("Personas detectadas por frame (YOLOv8)")
plt.savefig("grafico_personas.png")
plt.show()

print("✅ Gráfico guardado como grafico_personas.png")
