
# pip install VicksTor
# pip install stem

# from HostTor import VicksTor
# import VicksTor as vix

import os
from datetime import datetime
from flask import (
    Flask, 
    request, 
    jsonify, 
    render_template, 
    send_from_directory
)

# import darkweb as vix
# vix.run_server()
app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media/screenshots')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    """Handle screenshot upload."""
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return jsonify({
        "message": "File uploaded successfully", 
        "url": f"/media/screenshots/{file.filename}"
    })

@app.route('/list_screenshots', methods=['GET'])
def list_screenshots():
    """Fetch and display uploaded screenshots."""
    screenshots = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('jpg', 'jpeg', 'png')):
            screenshots.append({
                'filename': filename,
                'url': f"/media/screenshots/{filename}"
            })
    # screenshots.reverse()
    return jsonify(screenshots)

@app.route('/datatable', methods=['GET'])
def render_screenshots_page():
    """Render the HTML page for displaying screenshots."""
    return render_template('screenshots.html')

@app.route('/')
def home():
    """Render the main page with dynamic images."""
    # Build the list of images
    
    screenshots = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('jpg', 'jpeg', 'png')):
            screenshots.append({
                'filename': filename,
                'url': f"/media/screenshots/{filename}"
            })

    # Sort images by date descending
    screenshots.sort(key=lambda x: x['url'], reverse=True)
    return render_template('index.html', images=screenshots)

@app.route('/media/screenshots/<filename>')
def serve_screenshot(filename):
    """Serve uploaded screenshot files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')
