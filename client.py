import os
import time
import requests
import cv2
from datetime import datetime
import schedule

SAVE_DIR = os.path.join(os.getcwd(), "media/screenshots")  # Ensure absolute path
UPLOAD_URL = "http://127.0.0.1:5000/upload_screenshot"

# UPLOAD_URL = "https://crmss.pythonanywhere.com/upload_screenshot" 
os.makedirs(SAVE_DIR, exist_ok=True)

# IP_WEBCAM_URL = "http://192.168.0.108:8080/video"
IP_WEBCAM_URL = "http://211.132.61.124/mjpg/video.mjpg"

# IP_WEBCAM_URL = 0 # here, 0 is the default camera index
camera = cv2.VideoCapture(IP_WEBCAM_URL)

# Initialize the camera immediately after imports
if not camera.isOpened():
    raise Exception("Error: Unable to access the camera. Please check if it's connected.")

time.sleep(2)  # Allow the camera to adjust
camera.read()

def take_camera_photo():
    """Capture a photo using the open camera and save it locally."""
    global camera
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SAVE_DIR, f"photo_{timestamp}.png")
    
    # Capture a single frame
    ret, frame = camera.read()
    if ret:
        cv2.imwrite(filepath, frame)
        print(f"\nPhoto saved to {filepath}")
    else:
        print("\nError: Failed to capture photo.")
        filepath = None

    return filepath

def upload_screenshot(filepath):
    """Upload the photo to the server."""
    if filepath is None:
        print("\nNo photo to upload.")
        return
    
    with open(filepath, "rb") as file:
        files = {"file": file}
        response = requests.post(UPLOAD_URL, files=files)
    if response.status_code == 200:
        print(f"\nPhoto {filepath} uploaded successfully!")
    else:
        print(f"\nFailed to upload {filepath}: {response.status_code} - {response.text}")

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
    # Release the camera when the program exits
    if camera.isOpened():
        camera.release()
    cv2.destroyAllWindows()
