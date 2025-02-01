from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import subprocess
import sys
import io
import locale

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
GENERATED_SLIDES_FOLDER = os.path.join(os.getcwd(), 'generated_slides')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(GENERATED_SLIDES_FOLDER, exist_ok=True)

# Set UTF-8 encoding for subprocess (Windows Fix)
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/upload', methods=['POST'])
def upload_file():
    print("\n📤 **Upload API Called!**")  
    print("🔍 **Checking received files and form data...**")

    if 'pdfFiles' not in request.files:
        print("❌ **No files received!**")
        return jsonify({"message": "No files part"}), 400

    files = request.files.getlist('pdfFiles')
    requires_abstraction = request.form.get('requiresAbstraction') == 'true'
    abstraction_text = request.form.get('abstractionText', "")
    mode = request.form.get('mode', "")
    templateNumber = request.form.get('templateNumber', "dark")

    if len(files) == 0:
        print("❌ **No PDF files selected!**")
        return jsonify({"message": "No PDF files selected"}), 400

    uploaded_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                file.save(filepath)
                uploaded_files.append(filepath)
                print(f"✅ **File saved:** {filepath}")

                # Run text-extract.py
                print(f"🔄 **Processing:** Extracting text from {filename}...")
                result = subprocess.run(
                    ['python', 'text-extract.py', filepath],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                if result.returncode != 0:
                    print(f"❌ **Error in text-extract.py:** {result.stderr}")
                    return jsonify({"message": "Error processing file"}), 500
                print("✅ **Text extraction completed successfully!**")

                # Run app1.py
                print("🔄 **Generating slides using app1.py...**")
                python_path = sys.executable
                result_app1 = subprocess.run(
                    [python_path, 'app1.py', str(requires_abstraction)],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                if result_app1.returncode != 0:
                    print(f"❌ **Error in app1.py:** {result_app1.stderr}")
                    return jsonify({"message": "Error generating slides"}), 500
                print("✅ **Slide generation completed successfully!**")

                # Run template-based.py
                print("🔄 **Creating PowerPoint presentation...**")
                result_template = subprocess.run(
                    [python_path, 'template-based.py', 'generated_slides/final_presentation_slides.txt', 'generated_slides/output_presentation_final.pptx',str(templateNumber)],
                    capture_output=True,
                    text=True,
                    encoding='utf-8',
                    errors='replace'
                )

                if result_template.returncode != 0:
                    print(f"❌ **Error in template-based.py:** {result_template.stderr}")
                    return jsonify({"message": "Error generating presentation"}), 500
                print("✅ **PowerPoint presentation generated successfully!**")

            except Exception as e:
                print(f"❌ **Exception occurred:** {str(e)}")
                return jsonify({"message": "Error saving file"}), 500

    return jsonify({
        "message": "✅ **Files uploaded and processed successfully!**",
        "files": uploaded_files,
        "requiresAbstraction": requires_abstraction,
        "abstractionText": abstraction_text,
        "mode": mode
    })

@app.route('/download_pptx', methods=['GET'])
def download_pptx():
    pptx_filename = "output_presentation_final.pptx"
    pptx_file_path = os.path.join(GENERATED_SLIDES_FOLDER, pptx_filename)

    if not os.path.exists(pptx_file_path):
        print("❌ **Error: PowerPoint file not found!**")
        return jsonify({"error": "File not found"}), 404

    print(f"📤 **Sending file:** {pptx_file_path}")
    return send_from_directory(directory=GENERATED_SLIDES_FOLDER, path=pptx_filename, as_attachment=True)

if __name__ == '__main__':
    # Set the default encoding to UTF-8 for the Flask app
    if sys.platform.startswith('win'):
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    print("🚀 **Flask server is running on http://0.0.0.0:5000/**")
    app.run(debug=True, host='0.0.0.0', port=5000)