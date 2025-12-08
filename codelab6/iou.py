import torch
from torchvision.models.detection import ssd300_vgg16, SSD300_VGG16_Weights
from ultralytics import YOLO
from PIL import Image

def iou(boxA, boxB):
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interArea = max(0, xB - xA) * max(0, yB - yA)
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    if (boxAArea + boxBArea - interArea) == 0:
        return 0

    return interArea / float(boxAArea + boxBArea - interArea)

image_path = "evidence/imagen.jpeg"
img = Image.open(image_path).convert("RGB")

weights = SSD300_VGG16_Weights.DEFAULT
ssd = ssd300_vgg16(weights=weights).eval()
preprocess = weights.transforms()

x = preprocess(img).unsqueeze(0)

with torch.no_grad():
    out_ssd = ssd(x)[0]

box_ssd = None
for box, score in zip(out_ssd["boxes"], out_ssd["scores"]):
    if score > 0.5:
        box_ssd = box.tolist()
        break

model_yolo = YOLO("yolov8n.pt")
results = model_yolo(image_path)

box_yolo = None
if results[0].boxes is not None and len(results[0].boxes) > 0:
    boxes_yolo = results[0].boxes.xyxy.cpu().numpy()
    box_yolo = boxes_yolo[0].tolist()

print("\nResultados:")
if box_ssd and box_yolo:
    iou_value = iou(box_ssd, box_yolo)
    print("Caja SSD:", box_ssd)
    print("Caja YOLO:", box_yolo)
    print("IoU:", iou_value)
else:
    print("No se detectaron cajas suficientes para calcular IoU")
