import os
import httpx

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "nomic-embed-text"
GEN_MODEL = "llama3.1"
LLM_TIMEOUT = 120

async def retrieve_chunks(query: str, ollama_url: str, chroma_client) -> list[str]:
    collection = chroma_client.get_collection("scripts")
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/embed",
            json={"model":EMBED_MODEL, "input": query}
        )
        embedding = response.json()["embeddings"][0]
        results = collection.query(
            query_embeddings=[embedding],
            n_results=5
        )
        return results["documents"][0]
    
async def generate_answer(chunks: list[str], query:str, ollama_url: str, ) -> str:
    context = "\n\n".join(chunks)
    prompt = (
        f"Use the following passages from the script to answer the question.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n"
        f"Answer: "
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/generate",
            json={"model":GEN_MODEL, 
                  "prompt": prompt,
                  "stream": False},
            timeout=LLM_TIMEOUT
        )
        return response.json()["response"]