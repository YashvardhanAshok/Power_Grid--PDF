"""
Friday v2 — Backend
Flask + SQLite (users, db_groups, indexed_files) + ChromaDB + Ollama
"""

import os, json, time, hashlib, logging, sqlite3, secrets
from pathlib import Path
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

from flask import Flask, request, jsonify, Response, stream_with_context, g, send_from_directory, abort
from flask_cors import CORS
import fitz                          # PyMuPDF
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import requests as http_req

# ── Config ────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger(__name__)

OLLAMA_URL   = os.getenv("OLLAMA_URL",  "http://127.0.0.1:11434")
CHROMA_PATH  = os.getenv("CHROMA_PATH", "./chroma_db")
DB_PATH      = os.getenv("DB_PATH",     "./friday.db")
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
CHUNK_SIZE   = 800
CHUNK_OVERLAP= 100
TOP_K        = 6
SESSION_TTL  = 86400   # 24 h
OLLAMA_TIMEOUT = int(os.getenv("OLLAMA_TIMEOUT", "180"))
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "512"))
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "512"))
OLLAMA_NUM_BATCH = int(os.getenv("OLLAMA_NUM_BATCH", "16"))

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True)

# Serve the browser app from the Flask server so http://127.0.0.1:5000 works.
@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "login.html")

@app.route("/<path:path>")
def serve_frontend_asset(path):
    if path.startswith("api/"):
        abort(404)
    if (FRONTEND_DIR / path).is_file():
        return send_from_directory(FRONTEND_DIR, path)
    return send_from_directory(FRONTEND_DIR, "index.html")

# ── Singletons ────────────────────────────────────────────────────────────────
_embedder: Optional[SentenceTransformer] = None
_chroma:   Optional[chromadb.PersistentClient]  = None

def get_embedder():
    global _embedder
    if _embedder is None:
        log.info("Loading embedding model…")
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

def get_chroma():
    global _chroma
    if _chroma is None:
        _chroma = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False),
        )
    return _chroma

def get_collection(name: str):
    return get_chroma().get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )

# ── SQLite helpers ────────────────────────────────────────────────────────────
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop("db", None)
    if db: db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name     TEXT NOT NULL,
                created  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sessions (
                token    TEXT PRIMARY KEY,
                user_id  INTEGER NOT NULL,
                expires  TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS db_groups (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                name        TEXT NOT NULL,
                color       TEXT DEFAULT '#5d62fb',
                chroma_name TEXT NOT NULL UNIQUE,
                created     TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS indexed_files (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id    INTEGER NOT NULL,
                file_name   TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                file_hash   TEXT NOT NULL,
                pages       INTEGER,
                size_kb     REAL,
                created_date TEXT,
                indexed_at  TEXT NOT NULL,
                UNIQUE(group_id, file_hash)
            );
        """)
        db.commit()
        # Create default user if none exist
        row = db.execute("SELECT id FROM users LIMIT 1").fetchone()
        if not row:
            pw_hash = hashlib.sha256("friday123".encode()).hexdigest()
            db.execute(
                "INSERT INTO users (username, password, name, created) VALUES (?,?,?,?)",
                ("yash", pw_hash, "Yash", datetime.utcnow().isoformat()),
            )
            db.commit()
            log.info("Default user created: yash / friday123")

# ── Auth helpers ──────────────────────────────────────────────────────────────
def create_session(user_id: int) -> str:
    db = get_db()
    token = secrets.token_hex(32)
    expires = (datetime.utcnow() + timedelta(seconds=SESSION_TTL)).isoformat()
    db.execute("INSERT INTO sessions (token, user_id, expires) VALUES (?,?,?)",
               (token, user_id, expires))
    db.commit()
    return token

def get_current_user():
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    if not token:
        token = request.cookies.get("session_token", "")
    if not token:
        return None
    db = get_db()
    row = db.execute(
        "SELECT u.* FROM users u JOIN sessions s ON s.user_id=u.id "
        "WHERE s.token=? AND s.expires > ?",
        (token, datetime.utcnow().isoformat()),
    ).fetchone()
    return row

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({"error": "Unauthorized"}), 401
        g.user = user
        return f(*args, **kwargs)
    return wrapper

# ── Utility ───────────────────────────────────────────────────────────────────
def chunk_text(text: str):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + CHUNK_SIZE])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return [c.strip() for c in chunks if c.strip()]

def pdf_meta(path: str) -> dict:
    doc = fitz.open(path)
    text = "\n".join(p.get_text() for p in doc)
    st = os.stat(path)
    meta = {
        "pages": len(doc),
        "created_date": datetime.fromtimestamp(st.st_ctime).isoformat(),
        "size_kb": round(st.st_size / 1024, 1),
    }
    doc.close()
    return {"text": text, **meta}

def file_hash(path: str) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()

def ollama_stream(model: str, prompt: str):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True,
        "options": {
            "temperature": 0.2,
            "num_predict": OLLAMA_NUM_PREDICT,
            "num_ctx": OLLAMA_NUM_CTX,
            "num_batch": OLLAMA_NUM_BATCH,
        },
    }
    with http_req.post(
        f"{OLLAMA_URL}/api/generate",
        json=payload,
        stream=True,
        timeout=(10, OLLAMA_TIMEOUT),
    ) as r:
        try:
            r.raise_for_status()
        except http_req.HTTPError as e:
            detail = r.text.strip()
            raise RuntimeError(f"Ollama request failed: {detail or e}") from e

        for line in r.iter_lines():
            if not line:
                continue
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(f"Ollama returned invalid JSON: {line[:200]!r}") from e

            if chunk.get("error"):
                raise RuntimeError(f"Ollama error: {chunk['error']}")
            if chunk.get("response"):
                yield chunk["response"]
            if chunk.get("done"):
                break

def ollama_call(model: str, prompt: str) -> str:
    return "".join(ollama_stream(model, prompt))

# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json(force=True)
    username = data.get("username","").strip().lower()
    password  = data.get("password","").strip()
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    db = get_db()
    user = db.execute(
        "SELECT * FROM users WHERE username=? AND password=?", (username, pw_hash)
    ).fetchone()
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    token = create_session(user["id"])
    return jsonify({"token": token, "name": user["name"], "username": user["username"]})

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json(force=True)
    username = data.get("username","").strip().lower()
    password  = data.get("password","").strip()
    name      = data.get("name","").strip()
    if not all([username, password, name]):
        return jsonify({"error": "All fields required"}), 400
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    db = get_db()
    try:
        db.execute(
            "INSERT INTO users (username, password, name, created) VALUES (?,?,?,?)",
            (username, pw_hash, name, datetime.utcnow().isoformat()),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return jsonify({"error": "Username already taken"}), 409
    user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
    token = create_session(user["id"])
    return jsonify({"token": token, "name": user["name"], "username": user["username"]})

@app.route("/api/auth/logout", methods=["POST"])
@require_auth
def logout():
    token = request.headers.get("Authorization","").replace("Bearer ","")
    get_db().execute("DELETE FROM sessions WHERE token=?", (token,))
    get_db().commit()
    return jsonify({"status": "ok"})

@app.route("/api/auth/me", methods=["GET"])
@require_auth
def me():
    u = g.user
    return jsonify({"id": u["id"], "name": u["name"], "username": u["username"]})

# ── Ollama models ──────────────────────────────────────────────────────────────
@app.route("/api/models", methods=["GET"])
@require_auth
def list_models():
    try:
        r = http_req.get(f"{OLLAMA_URL}/api/tags", timeout=4)
        models = [
            {"name": m["name"], "size": m.get("size", 0),
             "modified": m.get("modified_at", "")}
            for m in r.json().get("models", [])
        ]
        return jsonify({"models": models, "ollama_running": True})
    except Exception as e:
        return jsonify({"models": [], "ollama_running": False, "error": str(e)})

# ── DB Groups (named vector databases) ───────────────────────────────────────
@app.route("/api/groups", methods=["GET"])
@require_auth
def list_groups():
    db = get_db()
    rows = db.execute(
        "SELECT g.*, COUNT(f.id) as file_count FROM db_groups g "
        "LEFT JOIN indexed_files f ON f.group_id=g.id "
        "WHERE g.user_id=? GROUP BY g.id ORDER BY g.created DESC",
        (g.user["id"],),
    ).fetchall()
    result = []
    for r in rows:
        coll = get_collection(r["chroma_name"])
        result.append({
            "id": r["id"],
            "name": r["name"],
            "color": r["color"],
            "chroma_name": r["chroma_name"],
            "file_count": r["file_count"],
            "chunk_count": coll.count(),
            "created": r["created"],
        })
    return jsonify({"groups": result})

@app.route("/api/groups", methods=["POST"])
@require_auth
def create_group():
    data = request.get_json(force=True)
    name  = data.get("name","").strip()
    color = data.get("color","#5d62fb").strip()
    if not name:
        return jsonify({"error": "Name required"}), 400
    chroma_name = f"user{g.user['id']}_{name.lower().replace(' ','_')}_{int(time.time())}"
    db = get_db()
    db.execute(
        "INSERT INTO db_groups (user_id, name, color, chroma_name, created) VALUES (?,?,?,?,?)",
        (g.user["id"], name, color, chroma_name, datetime.utcnow().isoformat()),
    )
    db.commit()
    row = db.execute("SELECT * FROM db_groups WHERE chroma_name=?", (chroma_name,)).fetchone()
    get_collection(chroma_name)  # create the chroma collection
    return jsonify({"id": row["id"], "name": row["name"], "color": row["color"],
                    "chroma_name": chroma_name, "file_count": 0, "chunk_count": 0})

@app.route("/api/groups/<int:gid>", methods=["DELETE"])
@require_auth
def delete_group(gid):
    db = get_db()
    row = db.execute("SELECT * FROM db_groups WHERE id=? AND user_id=?",
                     (gid, g.user["id"])).fetchone()
    if not row:
        return jsonify({"error": "Not found"}), 404
    try:
        get_chroma().delete_collection(row["chroma_name"])
    except Exception:
        pass
    db.execute("DELETE FROM indexed_files WHERE group_id=?", (gid,))
    db.execute("DELETE FROM db_groups WHERE id=?", (gid,))
    db.commit()
    return jsonify({"status": "deleted"})

# ── Scan ──────────────────────────────────────────────────────────────────────
@app.route("/api/scan", methods=["POST"])
@require_auth
def scan():
    data = request.get_json(force=True)
    folder = data.get("folder_path","").strip()
    if not folder or not os.path.isdir(folder):
        return jsonify({"error": f"Directory not found: {folder}"}), 400
    files = []
    for p in Path(folder).rglob("*.pdf"):
        try:
            st = os.stat(p)
            files.append({
                "file": p.name,
                "file_path": str(p),
                "created_date": datetime.fromtimestamp(st.st_ctime).isoformat(),
                "size_kb": round(st.st_size / 1024, 1),
            })
        except Exception:
            pass
    return jsonify({"count": len(files), "files": files})

# ── Index ─────────────────────────────────────────────────────────────────────
@app.route("/api/index", methods=["POST"])
@require_auth
def index_docs():
    data  = request.get_json(force=True)
    paths = data.get("file_paths", [])
    gid   = data.get("group_id")
    if not paths or not gid:
        return jsonify({"error": "file_paths and group_id required"}), 400
    db = get_db()
    group = db.execute("SELECT * FROM db_groups WHERE id=? AND user_id=?",
                       (gid, g.user["id"])).fetchone()
    if not group:
        return jsonify({"error": "Group not found"}), 404
    collection = get_collection(group["chroma_name"])
    embedder   = get_embedder()

    def generate():
        total = len(paths)
        indexed = skipped = 0
        for i, path in enumerate(paths):
            if not os.path.exists(path):
                yield json.dumps({"type":"skip","file":path,"reason":"not found"})+"\n"; skipped+=1; continue
            try:
                fh = file_hash(path)
                if db.execute("SELECT id FROM indexed_files WHERE group_id=? AND file_hash=?",
                              (gid, fh)).fetchone():
                    yield json.dumps({"type":"skip","file":Path(path).name,"reason":"already indexed"})+"\n"
                    skipped+=1; continue
                info   = pdf_meta(path)
                chunks = chunk_text(info["text"])
                if not chunks:
                    yield json.dumps({"type":"skip","file":Path(path).name,"reason":"no text"})+"\n"
                    skipped+=1; continue
                embs = embedder.encode(chunks).tolist()
                ids  = [f"{fh}_{j}" for j in range(len(chunks))]
                metas= [{"file": Path(path).name, "file_path": path,
                         "file_hash": fh, "chunk_index": j} for j in range(len(chunks))]
                for b in range(0, len(chunks), 100):
                    collection.upsert(ids=ids[b:b+100], embeddings=embs[b:b+100],
                                      documents=chunks[b:b+100], metadatas=metas[b:b+100])
                db.execute(
                    "INSERT OR IGNORE INTO indexed_files "
                    "(group_id,file_name,file_path,file_hash,pages,size_kb,created_date,indexed_at) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (gid, Path(path).name, path, fh, info["pages"],
                     info["size_kb"], info["created_date"], datetime.utcnow().isoformat()),
                )
                db.commit()
                indexed+=1
                yield json.dumps({"type":"progress","file":Path(path).name,
                                  "chunks":len(chunks),"done":i+1,"total":total})+"\n"
            except Exception as e:
                log.error(f"Index error {path}: {e}")
                yield json.dumps({"type":"error","file":path,"error":str(e)})+"\n"
        yield json.dumps({"type":"complete","indexed":indexed,"skipped":skipped,
                          "total_chunks":collection.count()})+"\n"

    return Response(stream_with_context(generate()), mimetype="application/x-ndjson")

# ── Search ────────────────────────────────────────────────────────────────────
@app.route("/api/search", methods=["POST"])
@require_auth
def search():
    data       = request.get_json(force=True)
    query      = data.get("query","").strip()
    group_ids  = data.get("group_ids", [])   # [] = all user groups
    file_names = data.get("file_names", [])
    top_k      = int(data.get("top_k", TOP_K))
    if not query:
        return jsonify({"error": "query required"}), 400

    db = get_db()
    if group_ids:
        groups = db.execute(
            f"SELECT * FROM db_groups WHERE id IN ({','.join('?'*len(group_ids))}) AND user_id=?",
            (*group_ids, g.user["id"]),
        ).fetchall()
    else:
        groups = db.execute("SELECT * FROM db_groups WHERE user_id=?",
                            (g.user["id"],)).fetchall()

    embedder = get_embedder()
    q_emb    = embedder.encode([query]).tolist()
    all_hits = []

    for grp in groups:
        coll = get_collection(grp["chroma_name"])
        if coll.count() == 0:
            continue
        where = None
        if file_names:
            where = {"file": {"$in": file_names}} if len(file_names) > 1 else {"file": {"$eq": file_names[0]}}
        kwargs = {"query_embeddings": q_emb,
                  "n_results": min(top_k, coll.count()),
                  "include": ["documents","metadatas","distances"]}
        if where:
            kwargs["where"] = where
        res = coll.query(**kwargs)
        for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
            all_hits.append({
                "file": meta["file"],
                "file_path": meta.get("file_path",""),
                "snippet": doc[:280].replace("\n"," "),
                "score": round(1 - dist, 4),
                "group_id": grp["id"],
                "group_name": grp["name"],
                "group_color": grp["color"],
            })

    all_hits.sort(key=lambda x: x["score"], reverse=True)
    matched_files = list({h["file"] for h in all_hits})
    return jsonify({"results": all_hits[:top_k*2], "matched_files": matched_files})

# ── Chat ──────────────────────────────────────────────────────────────────────
@app.route("/api/chat/stream", methods=["POST"])
@require_auth
def chat_stream():
    data       = request.get_json(force=True)
    message    = data.get("message","").strip()
    model      = data.get("model","gemma2:2b")
    group_ids  = data.get("group_ids", [])
    file_names = data.get("file_names", [])

    if not message:
        return jsonify({"error": "message required"}), 400

    db = get_db()
    context_chunks = []

    if group_ids:
        groups = db.execute(
            f"SELECT * FROM db_groups WHERE id IN ({','.join('?'*len(group_ids))}) AND user_id=?",
            (*group_ids, g.user["id"]),
        ).fetchall()
        embedder = get_embedder()
        q_emb    = embedder.encode([message]).tolist()
        for grp in groups:
            coll = get_collection(grp["chroma_name"])
            if coll.count() == 0:
                continue
            where = None
            if file_names:
                where = {"file": {"$in": file_names}} if len(file_names) > 1 else {"file": {"$eq": file_names[0]}}
            kwargs = {"query_embeddings": q_emb,
                      "n_results": min(TOP_K, coll.count()),
                      "include": ["documents"]}
            if where:
                kwargs["where"] = where
            res = coll.query(**kwargs)
            context_chunks.extend(res["documents"][0])

    if context_chunks:
        context_text = "\n\n---\n\n".join(context_chunks[:TOP_K])
        prompt = (
            f"You are Friday, an intelligent local document assistant.\n"
            f"Answer using the document context below. Be precise and concise.\n"
            f"If the answer isn't in the context, say so clearly.\n\n"
            f"[CONTEXT]\n{context_text}\n\n"
            f"[QUESTION]\n{message}\n\n[ANSWER]"
        )
    else:
        prompt = f"You are Friday, a helpful AI assistant.\nUser: {message}\nFriday:"

    def generate():
        yield f"data: {json.dumps({'type':'start','context_chunks':len(context_chunks)})}\n\n"
        tokens_sent = 0
        try:
            for token in ollama_stream(model, prompt):
                tokens_sent += 1
                yield f"data: {json.dumps({'type':'token','text':token})}\n\n"
        except Exception as e:
            log.exception("Chat stream failed")
            yield f"data: {json.dumps({'type':'error','text':str(e)})}\n\n"
            return
        if tokens_sent == 0:
            yield f"data: {json.dumps({'type':'error','text':'Ollama finished without returning any text. Try a larger model or restart Ollama.'})}\n\n"
            return
        yield f"data: {json.dumps({'type':'done'})}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

# ── Files in a group ──────────────────────────────────────────────────────────
@app.route("/api/groups/<int:gid>/files", methods=["GET"])
@require_auth
def group_files(gid):
    db = get_db()
    if not db.execute("SELECT id FROM db_groups WHERE id=? AND user_id=?",
                      (gid, g.user["id"])).fetchone():
        return jsonify({"error": "Not found"}), 404
    files = db.execute(
        "SELECT * FROM indexed_files WHERE group_id=? ORDER BY indexed_at DESC", (gid,)
    ).fetchall()
    return jsonify({"files": [dict(f) for f in files]})

# ── Health ────────────────────────────────────────────────────────────────────
@app.route("/api/health", methods=["GET"])
def health():
    try:
        r = http_req.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return jsonify({"status":"ok","ollama":True,"models":len(r.json().get("models",[]))})
    except:
        return jsonify({"status":"ok","ollama":False})

if __name__ == "__main__":
    init_db()
    log.info("Friday v2 backend → http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
