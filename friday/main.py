import os
import fitz  # PyMuPDF for PDF text extraction
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

# Paths
PDF_DIR = r"db\data\ACCOUNTANT"

# Load Sentence Transformer for vector embeddings
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Initialize ChromaDB for storing resume vectors
chroma_client = chromadb.PersistentClient(path="./resume_db")
collection = chroma_client.get_or_create_collection(name="resume_vectors")


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def is_resume(text):
    """Use an LLM to determine if a document is a resume."""
    response = ollama.chat(
        model="gemma:2b",
        messages=[{"role": "user", "content": f"Is this document a resume? Reply 'Yes' or 'No'.\n{text[:1000]}"}],
    )
    return "yes" in response["message"]["content"].lower()


def index_resumes(pdf_dir):
    """Extract text, filter resumes, generate embeddings, and store in ChromaDB."""
    for root, _, files in os.walk(pdf_dir):
        for file in files:
            if file.endswith(".pdf"):
                file_path = os.path.join(root, file)
                text = extract_text_from_pdf(file_path)
                if not text:
                    continue  # Skip empty PDFs
                
                # Check if it's a resume
                if not is_resume(text):
                    print(f"Skipping (Not a resume): {file}")
                    continue

                # Generate vector embeddings for resumes
                embedding = embedding_model.encode(text).tolist()
                collection.add(
                    ids=[file],
                    embeddings=[embedding],
                    metadatas=[{"file_name": file, "file_path": file_path, "text": text}],
                )
                print(f"Indexed Resume: {file}")





# **Run this once to index resumes**
index_resumes(PDF_DIR)

# **Example Queries**

