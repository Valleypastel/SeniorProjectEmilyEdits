from flask import Flask, request, jsonify
from flask_cors import CORS
import query_data

app = Flask(__name__)
CORS(app)

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

if __name__ == '__main__':
    app.run(debug=True)