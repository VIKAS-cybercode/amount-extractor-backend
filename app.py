
from flask import Flask, request, jsonify
from ocr_pipeline import process_text, process_image

app = Flask(__name__)

# Health check
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "service": "amount-extractor",
        "version": "1.0"
    })

# Text input endpoint
@app.route('/api/v1/extract/text', methods=['POST'])
def extract_text():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"status":"error","reason":"No text provided"}), 400
    result = process_text(data['text'])
    return jsonify(result)

# Image input endpoint
@app.route('/api/v1/extract/image', methods=['POST'])
def extract_image():
    if 'file' not in request.files:
        return jsonify({"status":"error","reason":"No file provided"}), 400
    file = request.files['file']
    result = process_image(file)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
