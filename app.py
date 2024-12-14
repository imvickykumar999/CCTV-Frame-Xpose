
# pip install VicksTor
# pip install stem

import os
from flask import (
    Flask, 
    request, 
    jsonify, 
    render_template, 
    send_from_directory
)

# from HostTor import VicksTor
# import VicksTor as vix

# vix.run_server('flask')
app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'media/screenshots')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB file size limit

@app.route('/upload_screenshot', methods=['POST'])
def upload_screenshot():
    """Handle screenshot upload."""
    if 'file' not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    # Save the file
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "url": f"/media/screenshots/{file.filename}"})

@app.route('/list_screenshots', methods=['GET'])
def list_screenshots():
    """Fetch and display uploaded screenshots."""
    screenshots = []
    for filename in os.listdir(app.config['UPLOAD_FOLDER']):
        if filename.endswith(('jpg', 'jpeg', 'png', 'gif')):
            screenshots.append({
                'filename': filename,
                'url': f"/media/screenshots/{filename}"
            })
    # screenshots.reverse()
    return jsonify(screenshots)

@app.route('/', methods=['GET'])
def render_screenshots_page():
    """Render the HTML page for displaying screenshots."""
    return render_template('screenshots.html')

@app.route('/media/screenshots/<filename>')
def serve_screenshot(filename):
    """Serve uploaded screenshot files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=False)
