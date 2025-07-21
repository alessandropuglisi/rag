import os
import streamlit as st
from openai import OpenAI
from pinecone import Pinecone

# Ottieni chiavi da secrets
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
PINECONE_API_KEY = st.secrets["PINECONE_API_KEY"]
PINECONE_ENV = st.secrets["PINECONE_ENV"]
PINECONE_INDEX_NAME = st.secrets["PINECONE_INDEX_NAME"]

# Inizializza i client
client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

# Embedding della query
def embed_text(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Ricerca dei testi rilevanti
def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embed_text(query)
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)
    return [match["metadata"]["text"] for match in results["matches"]]

# Costruzione e invio prompt
def generate_chatgpt_response(query):
    retrieved_texts = retrieve_relevant_chunks(query)
    context = "\n\n".join(retrieved_texts)
    prompt = f"Contesto:\n{context}\n\nDomanda: {query}\nRisposta:"

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Sei un assistente AI che risponde usando solo le informazioni fornite nel contesto."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=600
    )

    return response.choices[0].message.content
