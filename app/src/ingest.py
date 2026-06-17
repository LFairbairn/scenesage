import pymupdf
import os
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


def clean_text(text: str) -> str:
    paragraphs = text.split("\n\n")
    cleaned = [p.replace("\n", " ") for p in paragraphs]
    return "\n\n".join(cleaned)


def is_already_embedded(chroma_client, doc_hash) -> bool:
    collection = chroma_client.get_or_create_collection("scripts")
    results = collection.get(where={"doc_hash": doc_hash}, limit=1)
    return len(results["ids"]) > 0


def chunk_text(text: str, max_chars: int = 2000) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            chunks.append(paragraph)
        else:
            words = paragraph.split()
            current = []
            current_len = 0
            for word in words:
                if current_len + len(word) + 1 > max_chars:
                    chunks.append(" ".join(current))
                    current = []
                    current_len = 0
                current.append(word)
                current_len += len(word) + 1
            if current:
                chunks.append(" ".join(current))

    return chunks


async def embed_and_store(
    chunks: list[str], ollama_url: str, chroma_client, doc_hash: str
):
    collection = chroma_client.get_or_create_collection("scripts")
    async with httpx.AsyncClient() as client:
        for i, chunk in enumerate(chunks):
            response = await client.post(
                f"{ollama_url}/api/embed", json={"model": MODEL, "input": chunk}
            )
            data = response.json()
            if "embeddings" not in data:
                raise RuntimeError(f"Ollama embed request failed for chunk {i}: {data}")
            embedding = data["embeddings"][0]
            collection.add(
                ids=[f"{doc_hash}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"doc_hash": doc_hash}],
            )
