# Friday — Local PDF RAG Assistant

Friday is a local web application for searching and chatting with PDF documents. Create a document group, scan a folder of PDFs, index the files, then use either semantic search or Retrieval-Augmented Generation (RAG) chat to explore their contents.

The app runs locally and uses [Ollama](https://ollama.com/) for model inference.

## Features

- User registration and local session-based sign-in
- PDF folder scanning and batch indexing
- Named, color-coded document groups
- Semantic search across one or more groups
- RAG chat with streamed responses and retrieved-document context
- Local persistence with SQLite and ChromaDB
- Browser interface served directly by the Flask backend

## Tech stack

- **Backend:** Python, Flask, PyMuPDF, Sentence Transformers
- **Vector store:** ChromaDB
- **Database:** SQLite
- **LLM runtime:** Ollama
- **Frontend:** HTML, CSS, and vanilla JavaScript

## Prerequisites

- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed and running
- At least one Ollama model installed, for example:

  ```powershell
  ollama pull gemma2:2b
  ```

The first indexing or search request also downloads the `all-MiniLM-L6-v2` embedding model through Sentence Transformers if it is not already cached.

## Installation

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Start Ollama in a separate terminal if it is not already running:

```powershell
ollama serve
```

Then start Friday:

```powershell
python backend\app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## First use

1. Sign in with the default account on a fresh database:
   - Username: `yash`
   - Password: `friday123`
2. Alternatively, select **Create account** to register a local user.
3. Select an installed Ollama model from the model selector.
4. Create a database group from the sidebar.
5. Open **Manage databases**, enter the absolute folder path containing your PDFs, and scan it.
6. Select files and index them into the group.
7. Select one or more groups and choose either:
   - **RAG Chat** — ask questions and receive answers grounded in retrieved PDF content.
   - **Semantic** — find the most relevant PDF passages without generating an answer.

## Configuration

The backend accepts these optional environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama server URL |
| `CHROMA_PATH` | `./chroma_db` | Persistent ChromaDB directory |
| `DB_PATH` | `./friday.db` | SQLite database file |
| `OLLAMA_TIMEOUT` | `180` | Generation request timeout in seconds |
| `OLLAMA_NUM_PREDICT` | `512` | Maximum generated tokens |
| `OLLAMA_NUM_CTX` | `512` | Ollama context window setting |
| `OLLAMA_NUM_BATCH` | `16` | Ollama batch setting |

Example:

```powershell
$env:OLLAMA_NUM_PREDICT = "1024"
$env:OLLAMA_URL = "http://127.0.0.1:11434"
python backend\app.py
```

## Project structure

```text
backend/app.py       Flask API, PDF indexing, search, RAG chat, and frontend serving
frontend/            Login page and browser interface
data/                Sample/source PDF folders
chroma_db/           Persistent vector index (generated/runtime data)
friday.db            SQLite users, sessions, groups, and indexed-file metadata
requirements.txt     Python dependencies
```

## API overview

All application routes are served from `http://127.0.0.1:5000`.

- `POST /api/auth/login`, `POST /api/auth/register`, `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/models` and `GET /api/health`
- `GET`, `POST /api/groups`; `DELETE /api/groups/<id>`
- `POST /api/scan` and `POST /api/index`
- `POST /api/search`
- `POST /api/chat/stream` (Server-Sent Events)
- `GET /api/groups/<id>/files`

Protected endpoints require `Authorization: Bearer <token>`, supplied by the login endpoint and handled automatically by the frontend.

## Notes

- The folder scanner needs a path visible to the machine running Flask. On Windows, use a full path such as `D:\Documents\PDFs`.
- Indexed documents, user accounts, and sessions are kept locally in `chroma_db/` and `friday.db`.
- The built-in account and simple password hashing are intended for local development only. Change the default password or use a stronger authentication design before exposing this app to a network.
