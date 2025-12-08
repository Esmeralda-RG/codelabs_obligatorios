import time
import torch
from PIL import Image
from ultralytics import YOLO
from torchvision.models.detection import ssd300_vgg16, SSD300_VGG16_Weights
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

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

weights = SSD300_VGG16_Weights.DEFAULT
ssd = ssd300_vgg16(weights=weights).eval()
preprocess = weights.transforms()
yolo = YOLO("yolov8n.pt")
categories = weights.meta["categories"]

images = ["evidence/imagen1.jpeg", "evidence/imagen2.jpeg", "evidence/imagen3.jpeg"]

rows = []
headers = ["Imagen", "Tiempo SSD (s)", "Tiempo YOLO (s)", "Obj SSD", "Obj YOLO", "IoU"]

os.makedirs("resultados", exist_ok=True)

for img_path in images:
    img = Image.open(img_path).convert("RGB")

    x = preprocess(img).unsqueeze(0)
    t0 = time.time()
    with torch.no_grad():
        out_ssd = ssd(x)[0]
    t1 = time.time()

    time_ssd = t1 - t0
    scores_ssd = out_ssd["scores"]
    boxes_ssd = out_ssd["boxes"]
    labels_ssd = out_ssd["labels"]
    num_ssd = (scores_ssd > 0.5).sum().item()

    box_ssd = None
    for box, sc in zip(boxes_ssd, scores_ssd):
        if sc > 0.5:
            box_ssd = box.tolist()
            break

    fig, ax = plt.subplots(1, figsize=(8, 6))
    ax.imshow(img)
    for box, score, label in zip(boxes_ssd, scores_ssd, labels_ssd):
        if score > 0.5:
            x1, y1, x2, y2 = box.tolist()
            rect = patches.Rectangle(
                (x1, y1), x2 - x1, y2 - y1,
                linewidth=2, edgecolor="red", facecolor="none"
            )
            ax.add_patch(rect)
            ax.text(
                x1, y1,
                f"{categories[int(label)]} {score:.2f}",
                color="white",
                bbox=dict(facecolor="red", alpha=0.5)
            )
    ax.axis("off")
    ssd_out_path = f"resultados/ssd_{os.path.basename(img_path)}"
    plt.savefig(ssd_out_path, bbox_inches="tight")
    plt.close()

    t0 = time.time()
    results = yolo(img_path)
    t1 = time.time()

    time_yolo = t1 - t0
    num_yolo = len(results[0].boxes) if results[0].boxes is not None else 0

    box_yolo = None
    if results[0].boxes is not None and len(results[0].boxes) > 0:
        box_yolo = results[0].boxes.xyxy[0].cpu().numpy().tolist()

    yolo_out_path = f"resultados/yolo_{os.path.basename(img_path)}"
    results[0].save(filename=yolo_out_path)

    iou_value = "-"
    if box_ssd and box_yolo:
        iou_value = f"{iou(box_ssd, box_yolo):.3f}"

    rows.append([
        os.path.basename(img_path),
        f"{time_ssd:.3f}",
        f"{time_yolo:.3f}",
        str(num_ssd),
        str(num_yolo),
        iou_value
    ])

fig, ax = plt.subplots(figsize=(12, 5))
ax.axis("off")

table = ax.table(
    cellText=rows,
    colLabels=headers,
    loc="center",
    cellLoc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 1.5)

plt.title("Comparación SSD vs YOLO", pad=20)

output_image = "resultados/tabla_comparativa.png"
plt.savefig(output_image, bbox_inches="tight")
plt.close()

print(f"Imágenes guardadas en: carpeta 'resultados/'")
print(f"Tabla generada: {output_image}")
