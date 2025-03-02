from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import query_data
from populate_database import clear_database, reload_documents

app = Flask(__name__)
CORS(app)
DATA_FOLDER = os.path.abspath('data')

@app.route('/query', methods=['POST'])
def query():
    """Endpoint to handle user queries."""
    data = request.json
    user_query = data.get('query')
    if not user_query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = query_data.query_rag(user_query)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
  
@app.route('/get-files', methods=['GET'])   
def get_files():
    try:
        files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500    
     
@app.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename.endswith('.pdf'):
        file.save(os.path.join(DATA_FOLDER, file.filename))
        reload_documents()
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
            clear_database()
            #reload_documents()
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
    
@app.route('/files/<path:filename>')
def serve_file(filename):
    """Serve PDF files from the data directory."""
    return send_from_directory(DATA_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)