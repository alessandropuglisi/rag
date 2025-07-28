import pdfplumber
import docx
import os
import streamlit as st
import json
import tempfile
from google.cloud import storage
from openai import OpenAI
from pinecone import Pinecone

# Prendi le chiavi da Streamlit secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]
PINECONE_INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]
GCS_BUCKET_NAME = st.secrets["GCS_BUCKET_NAME"]

# Carica credenziali GCS dai secrets Streamlit
service_account_info = st.secrets["GCP_SERVICE_ACCOUNT"]

# Salva temporaneamente il file di credenziali
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
    json.dump(service_account_info, tmp)
    tmp.flush()
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = tmp.name

# Inizializza i client
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Estrazione testo
def extract_text_from_pdf(file_path):
    with pdfplumber.open(file_path) as pdf:
        return '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text())

def extract_text_from_doc(file_path):
    doc = docx.Document(file_path)
    return '\n'.join(p.text for p in doc.paragraphs)

# Embedding
def embed_text(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Indicizzazione
def add_document_to_index(doc_id, text):
    from uuid import uuid4

    max_chunk_tokens = 700
    words = text.split()
    chunks = [' '.join(words[i:i+max_chunk_tokens]) for i in range(0, len(words), max_chunk_tokens)]

    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        segment_id = f"{doc_id}_{i}".encode("ascii", errors="ignore").decode()  # Safe ID
        index.upsert(vectors=[(segment_id, embedding, {"text": chunk[:1000]})])  # limit metadata

# Scarica e indicizza documenti da GCS
def load_and_index_documents():
    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blobs = bucket.list_blobs()

    for blob in blobs:
        if blob.name.endswith((".pdf", ".docx", ".doc")):
            file_name = blob.name.split("/")[-1]
            blob.download_to_filename(file_name)

            if file_name.endswith(".pdf"):
                text = extract_text_from_pdf(file_name)
            else:
                text = extract_text_from_doc(file_name)

            print(f"Indicizzo: {file_name}")
            add_document_to_index(file_name.replace(" ", "_"), text)

if __name__ == "__main__":
    load_and_index_documents()
