import numpy as np
import cv2
import pyautogui  # For dynamically fetching screen resolution

confidenceThreshold = 0.5
NMSThreshold = 0.3

modelConfiguration = 'yolov3.cfg'
modelWeights = 'yolov3.weights'
labelsPath = 'coco.names'

labels = open(labelsPath).read().strip().split('\n')
np.random.seed(10)
COLORS = np.random.randint(0, 255, size=(len(labels), 3), dtype="uint8")

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
outputLayer = net.getLayerNames()

# https://stackoverflow.com/a/69941660/11493297
outputLayer = [outputLayer[i - 1] for i in net.getUnconnectedOutLayers()]

IP_WEBCAM_URL = "http://83.56.31.69/mjpg/video.mjpg" # Beach
# IP_WEBCAM_URL = "http://212.147.38.3/mjpg/video.mjpg" # 4 Way Road
# IP_WEBCAM_URL = "http://211.132.61.124/mjpg/video.mjpg" # Japan Bridge
# IP_WEBCAM_URL = "http://80.66.36.54/cgi-bin/faststream.jpg" # Austria Bridge
# IP_WEBCAM_URL = "http://93.87.72.254:8090/mjpg/video.mjpg" # Street Market
# IP_WEBCAM_URL = "http://192.168.0.108:8080/video" # IPV4 WebCam
# IP_WEBCAM_URL = 0 # Laptop Front WebCam

video_capture = cv2.VideoCapture(IP_WEBCAM_URL)
(W, H) = (None, None)

# Dynamically fetch screen resolution
screen_width, screen_height = pyautogui.size()  # Fetch laptop screen dimensions

while True:
    ret, frame = video_capture.read()
    if not ret:
        break  # Exit loop if the frame is not available
    
    if W is None or H is None:
        (H, W) = frame.shape[:2]

    blob = cv2.dnn.blobFromImage(frame, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)
    layersOutputs = net.forward(outputLayer)

    boxes = []
    confidences = []
    classIDs = []

    for output in layersOutputs:
        for detection in output:
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            if confidence > confidenceThreshold:
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype('int')
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    detectionNMS = cv2.dnn.NMSBoxes(boxes, confidences, confidenceThreshold, NMSThreshold)
    if len(detectionNMS) > 0:
        for i in detectionNMS.flatten():
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            color = [int(c) for c in COLORS[classIDs[i]]]
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            text = '{}: {:.4f}'.format(labels[classIDs[i]], confidences[i])
            cv2.putText(frame, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Resize the frame dynamically based on screen dimensions
    frame = cv2.resize(frame, (screen_width, screen_height))

    cv2.imshow('Output', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
