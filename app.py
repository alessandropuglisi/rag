import streamlit as st
import os

# Importa la funzione di risposta
from rag_chatbot import generate_chatgpt_response

# Streamlit UI
st.set_page_config(page_title="Chat con i tuoi documenti", layout="centered")
st.title("🗂️ Assistente AI sui tuoi documenti")

query = st.text_input("Fai una domanda sui documenti indicizzati:")

if st.button("Invia") and query.strip():
    with st.spinner("Sto cercando tra i documenti..."):
        try:
            response = generate_chatgpt_response(query)
            st.success("Risposta:")
            st.write(response)
        except Exception as e:
            st.error(f"Errore: {e}")
