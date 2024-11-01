#Last 2nd line to be changed

import cv2
import os
import numpy as np

MODEL_PATH = "MobileNetSSD_deploy.caffemodel"
PROTOTXT_PATH = "MobileNetSSD_deploy.prototxt"

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

def count_vehicles_in_image(image_path):
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]

    net = cv2.dnn.readNetFromCaffe(PROTOTXT_PATH, MODEL_PATH)
    blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    boxes = []
    confidences = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence > 0.5: 
            idx = int(detections[0, 0, i, 1])
            if CLASSES[idx] in ["car", "bus", "motorbike"]:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                boxes.append(box)
                confidences.append(float(confidence))

                cv2.rectangle(image, (startX, startY), (endX, endY), (0, 255, 0), 2)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    vehicle_count = len(indices)

    # Optionally show the output image (with bounding boxes) for confirmation
    # cv2.imshow("Detections", image)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return vehicle_count

def rename_images_with_vehicle_count(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith(".jpg") or filename.endswith(".png"): 
            image_path = os.path.join(folder_path, filename)
            vehicle_count = count_vehicles_in_image(image_path)

            new_filename = f"C{vehicle_count}_{filename}"
            new_image_path = os.path.join(folder_path, new_filename)

            os.rename(image_path, new_image_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

# Change path as per your pc
folder_path = r'c:\Users\utkar\Desktop\FULEQ\frames'
rename_images_with_vehicle_count(folder_path)
