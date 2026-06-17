import asyncio
import os
import chromadb
import streamlit as st
import hashlib
import tempfile
from app.src.ingest import (
    load_pdf,
    chunk_text,
    embed_and_store,
    is_already_embedded,
    clean_text,
)
from app.src.retrieval import retrieve_chunks, generate_answer

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")


def main():
    if "chroma_client" not in st.session_state:
        st.session_state.chroma_client = chromadb.PersistentClient(
            path="/app/data/chromadb"
        )
    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.title("SceneSage")
    st.markdown("""
    Hi, welcome to Scenesage! Upload a script and ask questions about its characters, scenes, and dialogue. 
    """)

    # File upload
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    if uploaded_file:
        if st.session_state.get("script_name") != uploaded_file.name:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(uploaded_file.getbuffer())
                tmp_path = tmp.name

            text = load_pdf(tmp_path)

            text = clean_text(text)

            doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

            if is_already_embedded(st.session_state.chroma_client, doc_hash):
                st.session_state.script_name = uploaded_file.name
                st.session_state.messages = []
                st.success(f"{uploaded_file.name} File already loaded.")
            else:
                chunks = chunk_text(text)
                asyncio.run(
                    embed_and_store(
                        chunks, OLLAMA_URL, st.session_state.chroma_client, doc_hash
                    )
                )
                st.session_state.script_name = uploaded_file.name
                st.session_state.messages = []
                st.success(f"{uploaded_file.name} loaded and ready!")

    if not st.session_state.get("script_name"):
        st.info("Upload a PDF script above to get started.")
        return

    st.markdown(f"**Loaded script:** {st.session_state.script_name}")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Ask a question about the script..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.spinner("Thinking..."):
            chunks = asyncio.run(
                retrieve_chunks(prompt, OLLAMA_URL, st.session_state.chroma_client)
            )
            answer = asyncio.run(generate_answer(chunks, prompt, OLLAMA_URL))

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.write(answer)


if __name__ == "__main__":
    main()
