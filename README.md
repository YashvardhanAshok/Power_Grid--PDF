# Friday v2

Modern local document intelligence — Flask + SQLite + ChromaDB + Ollama.

## Quick Start

### 1. Backend
```bash
cd friday-v2/backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
ollama serve                    # separate terminal
ollama pull gemma2:2b           # or any model
python app.py                   # → http://127.0.0.1:5000
```

### 2. Frontend
```bash
cd friday-v2/frontend
python -m http.server 8080      # → http://localhost:8080/login.html
```

Or just open `login.html` directly in your browser.

Default login: `yash` / `friday123`

---

## What's new in v2

| Feature | Details |
|---|---|
| **Login + Register** | SQLite-backed auth with session tokens |
| **Named database groups** | Create colour-coded groups, assign PDFs to them |
| **Model selector** | Shows all installed Ollama models with sizes |
| **Semantic search** | Click results to set context + switch to RAG |
| **Streaming chat** | Token-by-token SSE with context badge |
| **Sidebar layout** | Collapsible, persistent group selection |

---

## API Reference

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/auth/login` | ✗ | `{username, password}` |
| POST | `/api/auth/register` | ✗ | `{name, username, password}` |
| GET  | `/api/auth/me` | ✓ | Current user |
| GET  | `/api/models` | ✓ | Installed Ollama models |
| GET  | `/api/groups` | ✓ | User's database groups |
| POST | `/api/groups` | ✓ | Create group `{name, color}` |
| DELETE | `/api/groups/:id` | ✓ | Delete group + vectors |
| GET  | `/api/groups/:id/files` | ✓ | Files in group |
| POST | `/api/scan` | ✓ | `{folder_path}` → file list |
| POST | `/api/index` | ✓ | `{file_paths, group_id}` streams NDJSON |
| POST | `/api/search` | ✓ | `{query, group_ids, top_k}` |
| POST | `/api/chat/stream` | ✓ | SSE `{message, model, group_ids}` |
| GET  | `/api/health` | ✗ | Ollama status |
