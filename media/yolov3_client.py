import os
import time
import requests
import cv2
import numpy as np
from datetime import datetime
import schedule

# Directories and paths
SAVE_DIR = os.path.join(os.getcwd(), "screenshots")
os.makedirs(SAVE_DIR, exist_ok=True)

# YOLO configuration
modelConfiguration = 'yolov3.cfg'
modelWeights = 'yolov3.weights'
labelsPath = 'coco.names'

labels = open(labelsPath).read().strip().split('\n')
np.random.seed(10)
COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
outputLayer = net.getLayerNames()
outputLayer = [outputLayer[i - 1] for i in net.getUnconnectedOutLayers()]

# ngrok http --url=secure-bluegill-purely.ngrok-free.app 5000
# UPLOAD_URL = "https://secure-bluegill-purely.ngrok-free.app/upload_screenshot"
# UPLOAD_URL = "4k3cs34r5ycnbqaihxwa5m7e2eu4ilmxczrdolzu6taewecpl7w4w5id.onion/upload_screenshot"
# UPLOAD_URL = "https://crmss.pythonanywhere.com/upload_screenshot"
UPLOAD_URL = "http://127.0.0.1:5000/upload_screenshot"

# IP_WEBCAM_URL = "http://185.98.0.114:8888/mjpg/video.mjpg" # Wind Mill
# IP_WEBCAM_URL = "http://212.147.38.3/mjpg/video.mjpg" # 4 Way Road
IP_WEBCAM_URL = "http://211.132.61.124/mjpg/video.mjpg" # Japan Bridge
# IP_WEBCAM_URL = "http://80.66.36.54/cgi-bin/faststream.jpg" # Austria Bridge
# IP_WEBCAM_URL = "http://93.87.72.254:8090/mjpg/video.mjpg" # Street Market
# IP_WEBCAM_URL = "http://192.168.0.108:8080/video" # IPV4 WebCam
# IP_WEBCAM_URL = 0 # Laptop Front WebCam

camera = cv2.VideoCapture(IP_WEBCAM_URL)
if not camera.isOpened():
    raise Exception("Error: Unable to access the camera. Please check if it's connected.")

time.sleep(2)
camera.read()

def take_camera_photo():
    """Capture a photo using the open camera, run YOLO object detection, and save locally."""
    global camera
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SAVE_DIR, f"{timestamp}.png")

    ret, frame = camera.read()
    if ret:
        # frame = cv2.flip(frame, 1)  # Optional: flip the frame if needed

        # Prepare the frame for YOLO
        (H, W) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)
        layerOutputs = net.forward(outputLayer)

        # Initialize lists for detection results
        boxes = []
        confidences = []
        classIDs = []
        confidenceThreshold = 0.5
        NMSThreshold = 0.3

        # Process YOLO outputs
        for output in layerOutputs:
            for detection in output:
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]

                if confidence > confidenceThreshold:
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # Apply Non-Maximum Suppression
        detectionNMS = cv2.dnn.NMSBoxes(boxes, confidences, confidenceThreshold, NMSThreshold)
        if len(detectionNMS) > 0:
            for i in detectionNMS.flatten():
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                color = [int(c) for c in COLORS[classIDs[i]]]
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                text = f"{labels[classIDs[i]]}: {confidences[i]:.4f}"
                cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Save the processed frame
        cv2.imwrite(filepath, frame)
        print(f"\nPhoto with detections saved to {filepath}")
    else:
        print("\nError: Failed to capture photo.")
        filepath = None
    return filepath

def upload_screenshot(filepath):
    """Upload the screenshot to the server via the Tor network."""
    if not filepath:
        return
    with open(filepath, "rb") as file:
        files = {"file": file}
        proxies = {
            "http": "socks5h://127.0.0.1:9050",
            "https": "socks5h://127.0.0.1:9050",
        }
        try:
            response = requests.post(UPLOAD_URL, files=files, proxies=proxies, timeout=30)
            if response.status_code == 200:
                print(f"Screenshot {filepath} uploaded successfully!")
            else:
                print(f"Failed to upload {filepath}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            # print(f"Error during upload: {e}")
            pass

def job():
    """Take and upload a camera photo."""
    filepath = take_camera_photo()
    upload_screenshot(filepath)

schedule.every(10).seconds.do(job)
try:
    print("\nStarting the auto-camera photo uploader with YOLO detection...")
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if camera.isOpened():
        camera.release()
    cv2.destroyAllWindows()
