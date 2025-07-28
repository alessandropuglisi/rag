import streamlit as st
from rag_chatbot import generate_chatgpt_response

# Configura l'interfaccia web
st.set_page_config(page_title="RAG Chatbot", layout="wide")

# Titolo e descrizione
st.title("📚 Chatbot RAG - Ricerca nei Documenti")
st.write("🔍 Digita una domanda e ottieni una risposta basata sui documenti caricati.")

# Input dell'utente con text_area
query = st.text_area("📝 Inserisci una domanda:", height=100)

# Separatore visivo
st.markdown("---")

# Bottone per inviare la richiesta
if st.button("Cerca nei documenti"):
    if query.strip():  # controlla che non sia solo whitespace
        with st.spinner("🔄 Sto cercando nei documenti..."):
            response = generate_chatgpt_response(query)
        st.success("✅ Risposta generata!")
        st.write(f"🤖 **Risposta:** {response}")
    else:
        st.warning("⚠️ Inserisci una domanda prima di cercare.")
