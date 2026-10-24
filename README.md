# AI Knowledge Assistant Cloud Platform

Document question-answering platform with **embedding-based retrieval**, user authentication, PDF/TXT upload, conversation history, REST API, monitoring, and Docker deployment. Without an OpenAI API key, chat returns excerpts from your uploaded documents.

## Architecture

```
                    ┌─────────────┐
                    │   Internet  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Nginx    │  Reverse Proxy :80
                    │  (container)│
                    └──┬───────┬──┘
                       │       │
              /api/*   │       │  /*
                       │       │
              ┌────────▼──┐ ┌──▼──────────┐
              │  FastAPI  │ │ React SPA   │
              │  Backend  │ │  Frontend   │
              └─────┬─────┘ └─────────────┘
                    │
         ┌──────────┼──────────┐
         │          │          │
    ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐
    │PostgreSQL│ │ChromaDB│ │ Uploads │
    └─────────┘ └────────┘ └─────────┘
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| Backend | Python 3.11, FastAPI, SQLAlchemy (async) |
| AI / RAG | LangChain text splitters, Sentence Transformers |
| Vector DB | ChromaDB |
| Database | PostgreSQL 16 |
| Proxy | Nginx |
| Orchestration | Docker Compose |

## Features

- User registration & JWT authentication
- Embedding-based chatbot (RAG) with source citations
- PDF/TXT upload to personal knowledge base
- Conversation history persisted in PostgreSQL
- REST API with OpenAPI docs (`/docs`)
- Monitoring dashboard & Prometheus metrics
- Dockerized multi-container deployment

## Quick Start (Docker)

Prerequisites: Docker Desktop in Linux-container mode (or Docker Engine with Compose v2), an available HTTP port, and enough memory for PostgreSQL, ChromaDB, and the embedding model (about 4 GB recommended). First startup downloads the embedding model and needs internet access.

```bash
# 1. Clone and configure
git clone https://github.com/Kikumpum/AI-Knowledge-Assistant-Cloud-Platform.git
cd AI-Knowledge-Assistant-Cloud-Platform
cp .env.example .env
# Edit .env: set SECRET_KEY and POSTGRES_PASSWORD

# 2. Build and run
docker compose config --quiet
docker compose up -d --build
docker compose ps

# 3. Open browser
# http://localhost
```

On PowerShell, use `Copy-Item .env.example .env` instead of `cp`. Keep `.env` private. Use a URL-safe PostgreSQL password containing letters, digits, `.`, `_`, `~`, or `-`, because Compose builds the backend database URL from this value. To use another host port, set `HTTP_PORT` in `.env` and open `http://localhost:<HTTP_PORT>`.

Default flow: Register → Upload documents → Start chat. The first backend startup may take several minutes while the model downloads. To inspect it, run `docker compose logs -f backend`.

### Verify the installation

```bash
curl http://localhost/health
curl http://localhost/api/health
python scripts/test_api.py http://localhost
```

The API script registers a test user, uploads a TXT file, exercises chat, and removes its document and conversation. The test user remains in the database. Replace the URL if `HTTP_PORT` differs.

### Development mode

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

Vite runs at `http://localhost:3000`; Nginx also serves it on `HTTP_PORT`. Both route `/api` to the backend inside Docker. Source files are mounted for live reload. Stop this stack with `docker compose -f docker-compose.yml -f docker-compose.dev.yml down`.

### Common configuration

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | JWT signing key; set a long random value. |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Database credentials. |
| `HTTP_PORT` | Host HTTP port; default `80`. |
| `MAX_UPLOAD_SIZE_MB` | Maximum PDF/TXT upload size; default `10`. |
| `CORS_ORIGINS` | Comma-separated browser origins. |
| `USE_OPENAI`, `OPENAI_API_KEY`, `LLM_MODEL` | Optional generative answers. |

Compose sets `DATABASE_URL`, `CHROMA_HOST`, `CHROMA_PORT`, and `UPLOAD_DIR` for the backend container. Changing `POSTGRES_PASSWORD` after PostgreSQL initializes its volume does not change the existing database user's password; update the database credential or recreate the volume only if its data is disposable.

To stop the stack while preserving data, use `docker compose down`. Avoid `down -v` unless you intend to delete the PostgreSQL, ChromaDB, and upload volumes.

## Project Structure

```
.
├── backend/                 # FastAPI (clean architecture)
│   └── app/
│       ├── api/             # Routes & schemas
│       ├── application/     # Business logic (services)
│       ├── core/            # Config, security, logging
│       ├── domain/          # Entities
│       └── infrastructure/  # DB, ChromaDB, embeddings
├── frontend/                # React SPA
├── nginx/                   # Reverse proxy config
├── docs/                    # Deployment & security guides
├── scripts/                 # Server setup scripts
├── docker-compose.yml
└── .github/workflows/       # CI/CD
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register user |
| POST | `/api/auth/login` | Login (JWT) |
| GET | `/api/auth/me` | Current user |
| GET | `/api/chat/conversations` | List chats |
| POST | `/api/chat/conversations/{id}/messages` | Send message |
| POST | `/api/documents/upload` | Upload PDF/TXT |
| GET | `/api/monitoring/stats` | Dashboard stats |

## Documentation

- [Architecture & Components](docs/architecture.md)
- [Cloud Deployment Guide](docs/deployment.md)
- [Ubuntu Linux Server Setup](docs/linux-server-setup.md)
- [Security Best Practices](docs/security.md)

## Optional: OpenAI Integration

Set in `.env`:

```env
USE_OPENAI=true
OPENAI_API_KEY=sk-...
LLM_MODEL=gpt-3.5-turbo
```

Without OpenAI, the system uses retrieval-based answers from your uploaded documents.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Docker connection fails | Start Docker Desktop in Linux-container mode and check `docker info`. |
| Backend is unhealthy | Inspect `docker compose logs backend`; first launch downloads the embedding model. |
| Database or ChromaDB fails | Inspect `docker compose ps` and the corresponding service logs. |
| Port 80 is busy | Set `HTTP_PORT` in `.env` and restart Compose. |
| Upload is rejected | Use PDF/TXT below 10 MB or adjust `MAX_UPLOAD_SIZE_MB`. |
