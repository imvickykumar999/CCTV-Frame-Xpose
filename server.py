
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

import darkweb as vix
vix.run_server()
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
    search_query = request.args.get('search', '').lower()
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 8))

    # List all image files
    all_files = [
        {
            'filename': f, 
            'url': f"/media/screenshots/{f}",
            'last_modified': os.path.getmtime(os.path.join(app.config['UPLOAD_FOLDER'], f))
        }
        for f in os.listdir(app.config['UPLOAD_FOLDER']) 
        if f.endswith(('jpg', 'jpeg', 'png'))
    ]

    # Sort files by last modified timestamp (newest first)
    all_files.sort(key=lambda x: x['last_modified'], reverse=True)

    # Search filter
    if search_query:
        all_files = [f for f in all_files if search_query in f['filename'].lower()]

    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    paginated_files = all_files[start:end]

    return jsonify(paginated_files)

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
