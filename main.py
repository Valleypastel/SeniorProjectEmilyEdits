from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from query_data import query_rag
from populate_database import clear_database, reload_documents
import traceback

app = Flask(__name__)
CORS(app)
DATA_FOLDER = '/Users/sab/Desktop/SeniorProject/data'



@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()  # Ensure JSON data is received
        if not data or "question" not in data:
            return jsonify({"error": "Missing 'question' key in request"}), 400  # Return a clear error
        
        return jsonify(query_rag(data["question"]))  # Call the function with the question
    except Exception as e:
        print(f"🔥 ERROR: {e}")  # Print full error log in terminal
        return jsonify({"error": str(e)}), 500  # Return error to frontend


 # List all PDF files in the data folder   
@app.route('/get-files', methods=['GET'])   
def get_files():
    try:
        files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
    
 # Upload a PDF   
@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename.endswith('.pdf'):
        file.save(os.path.join(DATA_FOLDER, file.filename))
        return jsonify({'message': 'File uploaded successfully'}), 200
    return jsonify({'error': 'Only PDF files allowed'}), 400

@app.route('/delete-file', methods=['POST'])
def delete_file():
    """Endpoint to delete a PDF file from the server."""
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'No filename provided'}), 400

    file_path = os.path.join(DATA_FOLDER, filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            return jsonify({'message': f'{filename} deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'File not found'}), 404
    
@app.route('/update-database', methods=['POST'])
def update_database():
    """Endpoint to update Chroma database with new documents."""
    try:
        reload_documents()
        return jsonify({"message": "Database updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear-database', methods=['POST'])
def clear_chroma_database():
    """Endpoint to clear the Chroma database."""
    try:
        clear_database()
        return jsonify({"message": "Chroma database cleared successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)