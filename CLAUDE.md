# SceneSage — Project Spec

A locally-running RAG (Retrieval-Augmented Generation) tool for analysing film scripts.

## Tech Stack

| Tool | Purpose |
|---|---|
| Python | Primary language |
| UV | Package and project management |
| Streamlit | Web UI |
| PyMuPDF (`fitz`) | PDF text extraction |
| ChromaDB | Vector database (in-process, persisted via Docker volume) |
| Ollama — `nomic-embed-text` | Local embeddings model |
| Ollama — `llama3.1` | Local chat LLM |
| httpx | Async HTTP client for Ollama API |
| Docker + Docker Compose | Containerisation |
| pytest | Unit and integration tests |
| Playwright | End-to-end UI tests |
| Black | Code formatter |
| GitHub Actions | CI pipeline |
| RAGAS | RAG response evaluation (phase 2) |
| Taskipy | Task shortcuts |

## Architecture

One Docker service (Streamlit app). Ollama runs natively on host — same reason as DataPilot (Apple Silicon GPU access).

| Component | Runs in | Notes |
|---|---|---|
| Streamlit + ChromaDB + PyMuPDF | Docker | Single service |
| Ollama | Native on host | `nomic-embed-text` + `llama3.1` |

> **Note:** Ollama runs natively rather than in Docker because Docker's Linux VM layer prevents it from accessing Apple Silicon's GPU on M1/M2/M3 Macs, making inference unacceptably slow. This is the same decision made in DataPilot.

ChromaDB runs in-process inside the Streamlit container. Embeddings are persisted to a named Docker volume so re-uploading the same script does not require re-embedding.


## Project Layout
```
scenesage/
├── docker-compose.yml
├── pyproject.toml
├── CLAUDE.md
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── Dockerfile
│   └── src/
│       ├── app.py           # Streamlit UI
│       ├── ingest.py        # PDF parsing and embedding
│       └── retrieval.py     # Vector search and RAG chain
├── tests/
│   ├── test_ingest.py
│   ├── test_retrieval.py
│   └── e2e/
│       └── test_ui.py       # Playwright end-to-end tests
└── data/
    └── scripts/             # Sample PDF scripts (gitignored)
```

---

## How to run it
- to be confirmed as code is written

## How to test it
- Add taskipy commands when ready

## CI/Conventions
- Github Actions to be used when initialised.
- Follow industry level testing standards
- 100% Code covereage on unit testing - ingest.py and retrieval.py
- Integration tests where applicable
- E2E test when project is built
- Working up to date version on Git
- Do not introduce breaking changes to Git Repo

