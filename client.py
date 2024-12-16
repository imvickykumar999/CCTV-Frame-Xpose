import os
import time
import requests
import cv2
from datetime import datetime
import schedule

SAVE_DIR = os.path.join(os.getcwd(), "media/screenshots")
os.makedirs(SAVE_DIR, exist_ok=True)

# ngrok http --url=secure-bluegill-purely.ngrok-free.app 5000
# UPLOAD_URL = "https://secure-bluegill-purely.ngrok-free.app/upload_screenshot"
UPLOAD_URL = "4k3cs34r5ycnbqaihxwa5m7e2eu4ilmxczrdolzu6taewecpl7w4w5id.onion/upload_screenshot"
# UPLOAD_URL = "https://crmss.pythonanywhere.com/upload_screenshot"
# UPLOAD_URL = "http://127.0.0.1:5000/upload_screenshot"

IP_WEBCAM_URL = "http://83.56.31.69/mjpg/video.mjpg" # Beach
# IP_WEBCAM_URL = "http://212.147.38.3/mjpg/video.mjpg" # 4 Way Road
# IP_WEBCAM_URL = "http://211.132.61.124/mjpg/video.mjpg" # Japan Bridge
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
    """Capture a photo using the open camera and save it locally."""
    global camera
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SAVE_DIR, f"{timestamp}.png")
    
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(filepath, frame)
        print(f"\nPhoto saved to {filepath}")
    else:
        print("\nError: Failed to capture photo.")
        filepath = None
    return filepath

def upload_screenshot(filepath):
    """Upload the screenshot to the server via the Tor network."""
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
            pass

def job():
    """Take and upload a camera photo."""
    filepath = take_camera_photo()
    upload_screenshot(filepath)

schedule.every(10).seconds.do(job)
try:
    print("\nStarting the auto-camera photo uploader...")
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    print("\nExiting...")
finally:
    if camera.isOpened():
        camera.release()
    cv2.destroyAllWindows()
