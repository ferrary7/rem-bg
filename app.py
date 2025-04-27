# app.py
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
from werkzeug.utils import secure_filename
import tempfile
from scripts.remove_bg import remove_background_from_image

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/remove-background', methods=['POST'])
def remove_bg():
    # Check if file is in the request
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    # Check if the file has a name
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Create unique filenames with UUID
        unique_id = str(uuid.uuid4())
        
        # Create temp directory if it doesn't exist
        temp_dir = os.path.join(tempfile.gettempdir(), "bg_removal")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Set up input and output paths
        input_path = os.path.join(temp_dir, f"input_{unique_id}.png")
        output_path = os.path.join(temp_dir, f"output_{unique_id}.png")
        
        # Save uploaded file
        file.save(input_path)
        
        # Process the image using your existing function
        success = remove_background_from_image(input_path, output_path)
        
        if not success:
            return jsonify({"error": "Background removal failed"}), 500
        
        # Return the processed image as a response
        response = send_file(output_path, mimetype='image/png')
        
        # Clean up after sending the response
        @response.call_on_close
        def cleanup():
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)
        
        return response
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)