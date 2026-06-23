"""
SceneSage RAG Evaluation — Phase 2

Runs a set of known questions through the real pipeline (ingest → retrieve → generate),
then scores the results using RAGAS with a locally running Ollama LLM as the judge.

Requires Ollama running natively with nomic-embed-text and llama3.1 pulled.
Run from the project root: uv run task evaluate
"""

import asyncio
import hashlib
import os
import pathlib

import chromadb
from datasets import Dataset
from langchain_ollama import ChatOllama, OllamaEmbeddings
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)
from ragas.run_config import RunConfig

from app.src.ingest import (
    chunk_text,
    clean_text,
    embed_and_store,
    is_already_embedded,
    load_pdf,
)
from app.src.retrieval import generate_answer, retrieve_chunks

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
SCRIPT_PATH = (
    pathlib.Path(__file__).parent.parent / "tests" / "data" / "sample_script.pdf"
)

QUESTIONS = [
    "What does Maya say when she first gets on the radio?",
    "How many survivors are there?",
    "Who is Director Cole?",
    "What does Cole say when he hears the signal?",
    "What is Maya's condition when she enters the station?",
]

GROUND_TRUTHS = [
    "Maya says 'This is Maya Chen at station KRX-7. If anyone can hear this, we need help. The bridge is out. We have twelve survivors and two days of supplies. Please respond.'",
    "There are twelve survivors.",
    "Director Cole is the head of the Emergency Operations Centre, in his 50s with grey at his temples.",
    "Cole says 'Twelve survivors. Get me a helicopter and someone who knows the valley road. We move in twenty minutes.'",
    "Maya is breathing hard, wearing a muddy jacket, and her hands are shaking.",
]


async def run_pipeline():
    """Embed the sample script and run all questions through the real RAG pipeline."""
    chroma_client = chromadb.EphemeralClient()

    print("Loading and embedding sample script...")
    text = load_pdf(str(SCRIPT_PATH))
    text = clean_text(text)
    doc_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

    if not is_already_embedded(chroma_client, doc_hash):
        chunks = chunk_text(text)
        await embed_and_store(chunks, OLLAMA_URL, chroma_client, doc_hash)
    print("Script embedded.\n")

    questions, answers, all_contexts = [], [], []
    for i, question in enumerate(QUESTIONS, 1):
        print(f"[{i}/{len(QUESTIONS)}] {question}")
        contexts = await retrieve_chunks(question, OLLAMA_URL, chroma_client)
        answer = await generate_answer(contexts, question, OLLAMA_URL)
        print(f"    Answer: {answer}\n")
        questions.append(question)
        answers.append(answer)
        all_contexts.append(contexts)

    return questions, answers, all_contexts


def main():
    print("=" * 60)
    print("SceneSage RAGAS Evaluation — The Last Signal")
    print("=" * 60 + "\n")

    # Step 1: run the real pipeline and collect answers + retrieved contexts
    questions, answers, all_contexts = asyncio.run(run_pipeline())

    # Step 2: configure RAGAS to use local Ollama as the evaluator LLM
    print("Configuring RAGAS with local Ollama...\n")
    evaluator_llm = LangchainLLMWrapper(
        ChatOllama(model="llama3.1", base_url=OLLAMA_URL)
    )
    evaluator_embeddings = LangchainEmbeddingsWrapper(
        OllamaEmbeddings(model="nomic-embed-text", base_url=OLLAMA_URL)
    )

    # Assign the evaluator LLM to each metric
    faithfulness.llm = evaluator_llm
    context_precision.llm = evaluator_llm
    context_recall.llm = evaluator_llm
    answer_relevancy.llm = evaluator_llm
    answer_relevancy.embeddings = evaluator_embeddings

    # Step 3: build the HuggingFace Dataset RAGAS expects
    # ground_truths is a list of lists — RAGAS supports multiple references per question
    dataset = Dataset.from_dict(
        {
            "question": questions,
            "answer": answers,
            "contexts": all_contexts,
            "reference": GROUND_TRUTHS,
        }
    )

    # Step 4: run evaluation — llama3.1 acts as the judge for all four metrics.
    # max_workers=1 runs jobs sequentially so Ollama isn't overwhelmed by parallel requests.
    # timeout=300 gives each individual LLM call up to 5 minutes.
    print("Running RAGAS evaluation (this will take a few minutes)...\n")
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision, context_recall],
        run_config=RunConfig(timeout=300, max_workers=1),
    )

    print("\n" + "=" * 60)
    print("Results")
    print("=" * 60)
    print(result)


if __name__ == "__main__":
    main()
