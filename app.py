import os
import uuid
import base64
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  

UPLOAD_FOLDER = 'shared_images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

BASE_URL = "http://localhost:5000"


@app.route('/')
def index():
    """Serves the frontend interface."""
    return render_template('index.html')


@app.route('/save-image', methods=['POST'])
def save_image():
    """Accepts base64 image, saves it, and returns URLs."""
    try:
        data = request.json
        image_data = data.get('image')

        if not image_data:
            return jsonify({"error": "No image data provided"}), 400
        if "," in image_data:
            header, encoded = image_data.split(",", 1)
        else:
            encoded = image_data

        image_bytes = base64.b64decode(encoded)

        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        return jsonify({
            "download_url": f"{BASE_URL}/download/{filename}",
            "share_url": f"{BASE_URL}/share/{filename}"
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Downloads the file as an attachment."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/share/<filename>')
def share_file(filename):
    """Displays the image in browser for sharing preview."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True, port=5000)