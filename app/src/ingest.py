import pymupdf
import os
import chromadb
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = "nomic-embed-text"

def load_pdf(path: str) -> str:
    with pymupdf.open(path) as doc:
        text = chr(12).join([page.get_text() for page in doc])
    return text

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunk_convert = chunk_size * 4
    overlap_convert = overlap * 4
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + chunk_convert])
        start += chunk_convert - overlap_convert
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
