from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import subprocess
import sys

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
GENERATED_SLIDES_FOLDER = os.path.join(os.getcwd(), 'generated_slides')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_SLIDES_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    print("✅ Upload API Called!")  # Debugging log
    print("🔹 Received Files:", request.files)
    print("🔹 Form Data:", request.form)

    if 'pdfFiles' not in request.files:
        print("❌ No files received!")
        return jsonify({"message": "No files part"}), 400

    files = request.files.getlist('pdfFiles')
    requires_abstraction = request.form.get('requiresAbstraction') == 'true'
    abstraction_text = request.form.get('abstractionText', "")
    mode = request.form.get('mode', "")

    if len(files) == 0:
        print("❌ No PDF files selected!")
        return jsonify({"message": "No PDF files selected"}), 400

    uploaded_files = []
    
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                uploaded_files.append(filepath)
                print(f"✅ File saved at: {filepath}")

                # Trigger `text-extract.py`
                print(f"▶ Running text-extract.py with file: {filepath}")
                result = subprocess.run(['python', 'text-extract.py', filepath], capture_output=True, text=True)

                if result.returncode != 0:
                    print(f"❌ Error in text-extract.py: {result.stderr}")
                    return jsonify({"message": "Error processing file"}), 500
                
                # Trigger `app1.py`
                print("▶ Running app1.py")
                python_path = sys.executable  # Use correct Python interpreter
                result_app1 = subprocess.run([python_path, 'app1.py', str(requires_abstraction)], capture_output=True, text=True)

                if result_app1.returncode != 0:
                    print(f"❌ Error in app1.py: {result_app1.stderr}")
                    return jsonify({"message": "Error generating slides"}), 500
                
                # Trigger `template-based.py`
                print("▶ Running template-based.py")
                result_template = subprocess.run(
                    [python_path, 'template-based.py', 'generated_slides/final_presentation_slides.txt', 'generated_slides/output_presentation_final.pptx'],
                    capture_output=True,
                    text=True
                )

                if result_template.returncode != 0:
                    print(f"❌ Error in template-based.py: {result_template.stderr}")
                    return jsonify({"message": "Error generating presentation"}), 500

            except Exception as e:
                print(f"❌ Exception: {str(e)}")
                return jsonify({"message": "Error saving file"}), 500

    return jsonify({
        "message": "✅ Files uploaded successfully!",
        "files": uploaded_files,
        "requiresAbstraction": requires_abstraction,
        "abstractionText": abstraction_text,
        "mode": mode
    })

@app.route('/download_pptx', methods=['GET'])
def download_pptx():
    pptx_filename = "output_presentation_final.pptx"
    pptx_file_path = os.path.join(GENERATED_SLIDES_FOLDER, pptx_filename)

    # Check if the file exists before sending it
    if not os.path.exists(pptx_file_path):
        return jsonify({"error": "❌ File not found"}), 404

    print(f"✅ Sending file: {pptx_file_path}")
    return send_from_directory(directory=GENERATED_SLIDES_FOLDER, path=pptx_filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
