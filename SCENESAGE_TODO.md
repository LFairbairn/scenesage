# SceneSage TODO

## Project Setup
- [x] Create new GitHub repo — `scenesage`
- [x] Initialise project with UV (`pyproject.toml`)
- [x] Add dependencies (streamlit, pymupdf, chromadb, httpx, taskipy)
- [x] Add dev dependencies (pytest, pytest-asyncio, pytest-cov, black)
- [x] Configure Black target version (py312)
- [x] Create `CLAUDE.md`
- [x] Create `.gitignore` (data/scripts/, .venv/, __pycache__, .env, .DS_Store)

## Docker
- [x] Create `docker-compose.yml` — app service + named volume for ChromaDB
- [x] Create `app/Dockerfile`

## Core App — Ingest
- [x] Create `app/src/ingest.py` — PDF text extraction with PyMuPDF
- [x] Add text chunking (max 2000 chars per chunk)
- [ ] Add overlap between chunks to prevent character name / dialogue splits
- [x] Add `clean_text` — joins hard-wrapped PDF lines, removes mid-sentence line breaks before chunking
- [x] Add embedding via Ollama `nomic-embed-text`
- [x] Store chunks + embeddings in ChromaDB (persisted volume)
- [x] Add PDF Validation

## Core App — Retrieval
- [x] Create `app/src/retrieval.py` — similarity search against ChromaDB
- [x] Build RAG chain — retrieved chunks + question → Ollama llama3.1
- [x] Return plain English answer

## Streamlit UI
- [x] Create `app/src/main.py` — PDF upload, chat interface, session state (renamed from app.py to avoid sys.path collision with `app` package)
- [x] Display welcome message and upload prompt
- [x] Show success message on PDF ingested
- [x] Wire up chat input to retrieval chain

## Tests — Phase 1
- [x] Create `tests/test_ingest.py` — unit tests for PDF parsing and chunking
- [x] this validation unit test (pass a .txt path, assert it raises ValueError).
- [x] Create `tests/test_retrieval.py` — integration tests with real ChromaDB (mock with pytest-mock or is there in memory chromadb option? - fixture?)
- [x] Achieve 100% coverage of ingest.py and retrieval.py
- [x] Create a test aggregator for taskipy so one call runs: linting (ruff),black and tests.
- [x] Add tests for `is_already_embedded` (no match found, match found), `clean_text`, `chunk_text` word-split path, and `embed_and_store` bad Ollama response — 100% coverage restored
- [x] Add `conftest.py` with `chroma_client` fixture for test isolation (EphemeralClient shares global in-memory store; fixture deletes collection on teardown)


## CI
- [x] Create `.github/workflows/ci.yml` — lint + tests on push/PR
- [x] Add CI badge to README

## README
- [x] Write project overview, tech stack, architecture diagram
- [x] Add How to Run section (prerequisites: Docker, Ollama, nomic-embed-text, llama3.1)
- [x] Add screenshots

## Security
- [x] Prompt injection protection — prompt-level context sandboxing in `generate_answer`: retrieved chunks wrapped in `<script_excerpt>` tags with upfront instruction to treat content as data only, not commands

## Future Development Ideas
- **Multi-turn conversation memory** — `generate_answer` currently has no context of prior questions; each Q&A is independent. Would require passing conversation history into the prompt.
- **Multi-hop retrieval** — questions that span multiple scenes (e.g. "how can the dinosaurs reproduce if all female?" requires both the Wu chromosome explanation AND Grant's frog DNA explanation). Solutions: query decomposition, graph-based retrieval, or larger retrieval window.
- **Hybrid retrieval** — combine embedding similarity search with keyword search (BM25) for exact phrase lookup. Would fix cases like "spared no expense" where the phrase is buried in a semantically diverse chunk.
- **Chunk overlap** — prevent character name / dialogue splits at chunk boundaries.
- **Stage direction filtering** — strip `(stage directions)` from extracted text to reduce noise in embeddings.
- **Async concurrent embedding** — `embed_and_store` currently embeds chunks sequentially; `asyncio.gather` would parallelise Ollama requests and speed up ingestion of large scripts.
- **Token-aware chunking** — replace character-count approximation with a real tokenizer for more precise context window management.

## Phase 2 — Evaluation
- [x] Integrate RAGAS — `evaluation/evaluate.py` runs 5 questions through real pipeline and scores with llama3.1 as judge
- [x] Baseline scores on sample script (The Last Signal): faithfulness 0.77, answer_relevancy 0.80, context_precision 1.0, context_recall 1.0
- [ ] Display evaluation scores in UI or as a report
- [ ] Create `tests/e2e/test_ui.py` — Playwright end-to-end tests
- [ ] Update README with evaluation results

"What does Maya say when she first gets on the radio?"
"How many survivors are there?"
"Who is Director Cole?"
"What does Cole say when he hears the signal?"
"What is Maya's condition when she enters the station?"
