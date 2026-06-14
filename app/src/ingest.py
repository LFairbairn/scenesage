import pymupdf
import os
import chromadb
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = "nomic-embed-text"

def load_pdf(path: str) -> str:
    path = str(path)
    if not path.lower().endswith(".pdf"):
        raise ValueError("Invalid file type. Please upload a valid .pdf file")
    with pymupdf.open(path) as doc:
        text = chr(12).join([page.get_text() for page in doc])
    return text

def chunk_text(text: str) -> list[str]:
    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
    return chunks

async def embed_and_store(chunks: list[str], ollama_url: str, chroma_client):
    collection = chroma_client.get_or_create_collection("scripts")
    async with httpx.AsyncClient() as client:
        for i, chunk in enumerate(chunks):
            response = await client.post(
                f"{ollama_url}/api/embed",
                json={"model": MODEL, "input": chunk}
            )
            embedding = response.json()["embeddings"][0]
            collection.add(
                ids=[str(i)],
                embeddings=[embedding],
                documents=[chunk]
            )
