import cv2
import os
import numpy as np

# Paths to YOLOv4 model files
MODEL_PATH = "yolov3.weights"   
CONFIG_PATH = "yolov3.cfg"      
LABELS_PATH = "coco.names"       

# Load YOLO class labels
with open(LABELS_PATH, "r") as f:
    CLASSES = [line.strip() for line in f.readlines()]

# Load the YOLOv4 model
net = cv2.dnn.readNetFromDarknet(CONFIG_PATH, MODEL_PATH)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# Define the classes of interest (vehicles)
VEHICLE_CLASSES = {"car", "bus", "motorbike", "truck"}

def count_vehicles_in_image(image_path):
    # Load the image
    image = cv2.imread(image_path)
    (h, w) = image.shape[:2]

    # Prepare the image for YOLO
    blob = cv2.dnn.blobFromImage(image, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    # Get YOLO layer names and output layers
    ln = net.getLayerNames()
    ln = [ln[i - 1] for i in net.getUnconnectedOutLayers()]

    # Perform YOLO forward pass
    detections = net.forward(ln)

    boxes = []
    confidences = []
    vehicle_count = 0

    # Process each detection
    for output in detections:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            # Filter by confidence and vehicle classes
            if confidence > 0.5 and CLASSES[class_id] in VEHICLE_CLASSES:
                box = detection[0:4] * np.array([w, h, w, h])
                (centerX, centerY, width, height) = box.astype("int")

                # Get bounding box coordinates
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # Append to boxes and confidences
                boxes.append([x, y, width, height])
                confidences.append(float(confidence))

    # Apply Non-Max Suppression
    indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Draw bounding boxes for the remaining indices
    if len(indices) > 0:
        for i in indices.flatten():  # Use flatten to handle 1D array
            box = boxes[i]
            (x, y, width, height) = box

            # Draw the bounding box and label
            label = f"{CLASSES[np.argmax(confidences[i])]}: {confidences[i]:.2f}"
            cv2.rectangle(image, (x, y), (x + width, y + height), (0, 255, 0), 2)
            cv2.putText(image, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            vehicle_count += 1  # Count only the detected vehicles

    # Display the image (optional)
    #cv2.imshow("Detections", image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()

    return vehicle_count

def rename_images_with_vehicle_count(folder_path):
    # Iterate over each image in the folder
    for filename in os.listdir(folder_path):
        # Skip files that already start with 'C'
        if filename.startswith("C"):
            print(f"Skipping '{filename}' as it already starts with 'C'")
            continue

        if filename.endswith(".jpg") or filename.endswith(".png"):  # Process only image files
            image_path = os.path.join(folder_path, filename)
            vehicle_count = count_vehicles_in_image(image_path)

            # New filename format as "C_vehicleCount_ExistingName"
            new_filename = f"C{vehicle_count}_{filename}"
            new_image_path = os.path.join(folder_path, new_filename)

            # Rename the file
            os.rename(image_path, new_image_path)
            print(f"Renamed '{filename}' to '{new_filename}'")

# Usage
folder_path = r'.\frames'  # Specify the path to the folder containing images
rename_images_with_vehicle_count(folder_path)
