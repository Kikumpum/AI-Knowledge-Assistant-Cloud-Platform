# AI Chatbot Cloud

Production-ready AI chatbot platform with **embedding-based RAG**, user authentication, document upload (PDF/TXT), conversation storage, REST API, monitoring dashboard, and full **Docker + Nginx** deployment for Ubuntu cloud servers (AWS EC2 / Google Cloud).

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

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — set SECRET_KEY and POSTGRES_PASSWORD

# 2. Build and run
docker compose up -d --build

# 3. Open browser
# http://localhost
```

Default flow: Register → Upload documents → Start chat.

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

## License

MIT
