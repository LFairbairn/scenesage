**Project Approach & Collaboration with Claude Code**

**My Role & Experience:**
- Junior developer with limited full-stack experience
- Want to build this project to learn and grow
- Need guidance navigating architecture and code decisions

**How I Want to Work:**
- Move through development **slowly and deliberately**
- Do as much of the coding myself as possible
- Understand each decision and implementation before moving forward
- Not rush ahead - focus on learning over speed

**What I Need from Claude Code:**
- Act as **mentor/senior developer**, not just code generator
- **Explain the "why"** behind architectural and code decisions
- Help me understand what we're doing at each step
- Guide me through problems rather than solving them for me
- Review my code and suggest improvements
- Point me to best practices and resources

**Development Style:**
- Break down tasks into small, digestible chunks
- Pause for explanation and questions before moving to next step
- Let me attempt implementations first, then provide feedback
- Focus on understanding over completion speed

**Expected Outcome:**
- A working project I genuinely understand
- Portfolio piece I can confidently discuss in interviews
- Real learning experience, not just a completed codebase

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
│       ├── main.py          # Streamlit UI (entry point — named to avoid colliding with the `app` package on sys.path)
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
- use taskipy commands

## MCP Tools Available

- **context7** — use for up-to-date library documentation (PyMuPDF, ChromaDB, httpx, Streamlit, RAGAS). Prefer this over training knowledge for API lookups.
- **docker** — Docker management
- **fetch** — fetch web pages
- **playwright** — browser automation (phase 2 E2E tests)

## CI/Conventions
- Github Actions to be used when initialised.
- Follow industry level testing standards
- 100% Code covereage on unit testing - ingest.py and retrieval.py
- Integration tests where applicable
- E2E test when project is built
- Working up to date version on Git
- Do not introduce breaking changes to Git Repo

