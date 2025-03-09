from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from sentence_transformers import SentenceTransformer  
from ollama import chat
import chromadb
import webbrowser 

app = Flask(__name__, static_folder="Front End")
CORS(app)  

@app.route('/')
def serve_frontend():
    return send_from_directory("Front End", "index.html")

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory("Front End", path)

# Load embedding model amd Connect to ChromaDB 
model = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=r"db/vector_db")

try:
    collection = chroma_client.get_collection("pdf_embeddings")
except chromadb.errors.InvalidCollectionException:
    collection = chroma_client.create_collection("pdf_embeddings")

@app.route('/chat', methods=['POST'])
def chatbot():
    data = request.json
    user_message = data.get("message", "")
    modle_name = data.get("modle_name", "")
    use_dataset = data.get("use_dataset", False)

    def query_pdf_database(user_message):
        """Fetch relevant parts of the resume from the vector database."""
        query_embedding = model.encode(user_message).tolist()  
        results = collection.query(query_embeddings=[query_embedding], n_results=3)

        if results["documents"]:
            return "\n".join(results["documents"][0])  
        return "No relevant documents found."

    relevant_docs = query_pdf_database(user_message)

    try:
        if use_dataset and relevant_docs != "No relevant documents found.":
            prompt = f"Based on the following resume information, answer the user's question:\n\n{relevant_docs}\n\nQuestion: {user_message}"
        else:
            prompt = user_message  

        response = chat(model=modle_name, messages=[{"role": "user", "content": prompt}])

        return jsonify({"response": response.message.content})
    
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred while processing the request."}), 500

if __name__ == '__main__':
    port = 5000
    url = f"http://127.0.0.1:{port}/"

    webbrowser.open(url)
    app.run(debug=True, host='0.0.0.0', port=port)
