# YoutubeTranscriptRag

RAG demo with FastAPI, Qdrant, and Temporal.

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Python 3.12 (see `.python-version`)
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (for Qdrant, Temporal, and related services)

## Clone and setup

```bash
git clone https://github.com/singhsanket143/Youtube-Transcript-Naive-Rag-Python-Langchain-Temporal-GPT.git
cd YoutubeTranscriptRag

cp .env.example .env
# Edit .env and set OPENAI_API_KEY (required for RAG features)
```

Install dependencies and the project into a local virtual environment:

```bash
uv sync
```

## Download dataset

From the repository root, download the YouTube transcriptions dataset and export RAG-style CSV parts (written to `data/youtube_rag_full/` by default):

```bash
uv run export_all_youtube_rag_csvs.py
```

## Run the API locally

Start backing services (Qdrant, Postgres, Temporal, Temporal UI):

```bash
docker compose up -d
```

Run the FastAPI app on the host:

```bash
uv run youtubetranscriptrag
```

Or equivalently:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Open [http://localhost:8000/](http://localhost:8000/) — you should see `{"message":"Hello, World!"}`.

API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Useful URLs (Docker Compose)

| Service     | URL |
|------------|-----|
| API (local)| http://localhost:8000 |
| Qdrant     | http://localhost:6333 |
| Temporal UI| http://localhost:8080 |

Stop infrastructure:

```bash
docker compose down
```

To remove volumes as well:

```bash
docker compose down -v
```

## Run API and worker in Docker (optional)

The `api` and `worker` services use the Compose profile `app` and build from the repository root. When a `Dockerfile` is present:

```bash
docker compose --profile app up --build
```

Ensure `.env` exists (same as local setup). The API is exposed on port **8000**.

Stop everything:

```bash
docker compose --profile app down
```
