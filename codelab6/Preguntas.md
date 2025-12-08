# Detección de objetos con SSD 

## Imagen original para prueba inicial 
![](evidence/imagen.jpeg)

## Correr SSD en una imagen
[Ver reporte](./evidence/resultados_imagen.txt)

## Visualizar resultados de SSD
![](evidence/Figure_1.png)

## Comparación con YOLO-lite 
![](evidence/comparacion.jpg)

## Calcular IoU simple 
![](evidence/iou.jpg)

## Reto 

En este caso se seleccionaron 3 imagenes para la comparación, teniendo esta tabla como resultado:

![](resultados/tabla_comparativa.png)

Asímismo, se presenta a continuación la detección realizada por SSD y Yolo 

### Imagen 1 (SSD)
![](resultados/ssd_imagen1.jpeg)

### Imagen 1 (Yolo)
![](resultados/yolo_imagen1.jpeg)

### Imagen 2 (SSD)
![](resultados/ssd_imagen2.jpeg)

### Imagen 2 (Yolo)
![](resultados/yolo_imagen2.jpeg)

### Imagen 3 (SSD)
![](resultados/ssd_imagen3.jpeg)

### Imagen 3 (Yolo)
![](resultados/yolo_imagen3.jpeg)

## Modelo para proyecto 

Después de comparar ambos modelos en varias imágenes, YOLOv8 mostró tiempos de inferencia  menores que SSD, lo cual lo hace más adecuado para aplicaciones en tiempo real, al ser más eficiente y rápido. Además, en la imagen 2 logra detectar más objetos que SSD.


