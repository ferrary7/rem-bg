from flask import Flask, request, send_file, jsonify
import os
from backgroundremover.bg import remove

app = Flask(__name__)

@app.route('/remove-bg', methods=['POST'])
def remove_bg():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image_file = request.files['image']
    input_path = 'input.png'
    output_path = 'output.png'
    image_file.save(input_path)
    try:
        with open(input_path, "rb") as f:
            data = f.read()
        img = remove(data,
                    model_name="u2net",
                    alpha_matting=True,
                    alpha_matting_foreground_threshold=240,
                    alpha_matting_background_threshold=10,
                    alpha_matting_erode_structure_size=10,
                    alpha_matting_base_size=1000)
        with open(output_path, "wb") as f:
            f.write(img)
        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
