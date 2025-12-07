from ultralytics import YOLO

model_yolo = YOLO("yolov8n.pt")
results = model_yolo("imagen.jpeg")

results[0].show()

results[0].save(filename="comparacion.jpg")
