# Penjelasan Komponen Sistem

## 1. Nginx (Reverse Proxy)

**Fungsi:** Gerbang masuk tunggal dari internet. Memisahkan traffic frontend (`/`) dan API (`/api/`), menambahkan security headers, membatasi ukuran upload, dan menyembunyikan port internal container.

## 2. Frontend (React + Vite)

**Fungsi:** Antarmuka web responsif untuk login, chat, upload dokumen, dan dashboard monitoring. Berkomunikasi dengan backend via REST API dengan JWT Bearer token.

**Halaman utama:**
- `/login`, `/register` — autentikasi
- `/chat` — percakapan AI
- `/documents` — knowledge base
- `/monitoring` — statistik sistem

## 3. Backend (FastAPI)

**Fungsi:** REST API, autentikasi JWT, orchestrasi RAG, pengelolaan file, penyimpanan percakapan.

**Lapisan clean architecture:**
- `api/` — endpoint HTTP
- `application/` — logika bisnis (AuthService, ChatService, DocumentService, RAGService)
- `domain/` — entitas murni
- `infrastructure/` — PostgreSQL, ChromaDB, Sentence Transformers

## 4. PostgreSQL

**Fungsi:** Database relasional untuk users, conversations, messages, dan metadata dokumen. Data terstruktur dan durable.

## 5. ChromaDB

**Fungsi:** Vector database untuk menyimpan embedding chunk dokumen. Mendukung similarity search dengan filter `user_id` (isolasi multi-tenant).

## 6. Sentence Transformers

**Fungsi:** Model `all-MiniLM-L6-v2` untuk mengubah teks menjadi vektor 384 dimensi. Digunakan saat indexing dokumen dan saat query chat.

## 7. LangChain Text Splitter

**Fungsi:** Memecah dokumen panjang menjadi chunk dengan overlap agar konteks retrieval lebih baik.

## 8. RAG Pipeline

**Fungsi:** Retrieval-Augmented Generation — mencari chunk relevan dari knowledge base user, lalu menghasilkan jawaban berbasis konteks (dengan opsi OpenAI).

## 9. Docker Compose

**Fungsi:** Orkestrasi semua container, jaringan internal, volume persisten (postgres, chroma, uploads), health checks, dan restart policy.

## 10. GitHub Actions

**Fungsi:**
- **CI:** Validasi build frontend & syntax backend pada setiap push/PR
- **Deploy:** SSH ke server cloud, pull, rebuild containers (aktifkan dengan secret + `ENABLE_DEPLOY=true`)

## 11. Monitoring

**Fungsi:**
- Dashboard UI: jumlah user, conversation, message, document
- Health status ChromaDB & database
- Prometheus metrics endpoint untuk integrasi Grafana/Alertmanager
