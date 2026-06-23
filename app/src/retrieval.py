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
            f"{ollama_url}/api/embed", json={"model": EMBED_MODEL, "input": query}
        )
        embedding = response.json()["embeddings"][0]
        # n_results=15: long scripts repeat key phrases across many scenes; 5 was too few
        # to surface the most relevant chunk when the same line appears 4+ times.
        results = collection.query(query_embeddings=[embedding], n_results=15)
        # ChromaDB returns a list-of-lists (one per query); [0] selects our single query.
        return results["documents"][0]


async def generate_answer(
    chunks: list[str],
    query: str,
    ollama_url: str,
) -> str:
    context = "\n\n".join(chunks)
    # Prompt is tightly constrained to prevent the model falling back to training
    # data ("only use... nothing else") and to stop verbatim chunk reproduction
    # ("in your own words — do not copy").
    prompt = (
        f"Only use the following passages, and nothing else, from the script to answer the question. "
        f"Answer concisely in one or two sentences in your own words - do not copy or reproduce the passages directly. "
        f"If the answer is not found in the passages, say 'I can not find that in the script.'\n\n"
        f"{context}\n\n"
        f"Question: {query}\n"
        f"Answer: "
    )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ollama_url}/api/generate",
            json={"model": GEN_MODEL, "prompt": prompt, "stream": False},
            timeout=LLM_TIMEOUT,
        )
        return response.json()["response"]
