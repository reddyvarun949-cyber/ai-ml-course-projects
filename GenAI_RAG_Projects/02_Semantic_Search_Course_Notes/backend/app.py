"""Flask API for the Semantic Search over Course Notes project.

Run from the project root:
    python backend/app.py
The API starts on http://localhost:5000

Endpoints
    GET  /api/health      -> is the API up? which embedding method? how many chunks?
    GET  /api/documents   -> titles and topics of all notes (the frontend builds the topic filter from this)
    POST /api/search      -> {"query": "...", "top_k": 1-10, "topic": optional} -> best matching chunks

The index (vectors + chunk metadata + fitted vectorizer/SVD) is built in notebook/Semantic_Search_Course_Notes.ipynb
and loaded ONCE when the server starts. Requests only embed the query and compare it with the stored vectors.

Optional: EMBEDDING_BACKEND=sentence-transformers uses a neural embedding model instead of LSA, if the
sentence-transformers library is installed (pip install sentence-transformers; the model downloads on first use).
The chunks are then re-embedded once at start-up. This option is documented but NOT tested in this project.
"""
import json
import os
import re
import sys

import joblib
from flask import Flask, jsonify, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import search_engine as se  # noqa: E402  (same chunking/tokenizing code the notebook used)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS = os.path.join(BASE_DIR, "models")
INFO_PATH = os.path.join(MODELS, "index_info.json")
EMB_PATH = os.path.join(MODELS, "embeddings.npy")
CHUNKS_PATH = os.path.join(MODELS, "chunks.json")

ALLOWED_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")
BACKEND = os.environ.get("EMBEDDING_BACKEND", "local").strip().lower()
MAX_TOP_K = 10

app = Flask(__name__)

# ---- load the index once at start-up ----
for path in (INFO_PATH, EMB_PATH, CHUNKS_PATH):
    if not os.path.exists(path):
        raise SystemExit(f"Index file {path} not found. Run notebook/Semantic_Search_Course_Notes.ipynb first.")
with open(INFO_PATH) as f:
    info = json.load(f)
store = se.VectorStore.load(EMB_PATH, CHUNKS_PATH)


def load_local_embedder():
    """Rebuild the embedder the notebook chose, from the saved fitted parts."""
    vectorizer = joblib.load(os.path.join(MODELS, "vectorizer.joblib"))
    method = info["embedding_method"]
    if method == "lsa":
        return se.LsaEmbedder(vectorizer=vectorizer, svd=joblib.load(os.path.join(MODELS, "svd.joblib")))
    if method == "tfidf":
        return se.TfidfEmbedder(vectorizer=vectorizer)
    return se.KeywordEmbedder(vectorizer=vectorizer)


if BACKEND == "sentence-transformers":
    try:
        embedder = se.SentenceTransformerEmbedder(os.environ.get("ST_MODEL", "all-MiniLM-L6-v2"))
    except ImportError:
        raise SystemExit("EMBEDDING_BACKEND=sentence-transformers but the library is not installed. "
                         "Run: pip install sentence-transformers   (or unset EMBEDDING_BACKEND to use LSA).")
    # The saved vectors belong to LSA, so re-embed the same chunks with the neural model (once, at start-up).
    store = se.VectorStore(embedder.encode([se.text_for_embedding(c) for c in store.chunks]), store.chunks)
    METHOD_NAME = f"sentence-transformers ({embedder.model_name})"
    # Neural cosine scores have a different scale: choose this threshold yourself (notebook section 7).
    MIN_CONFIDENCE = float(os.environ.get("ST_MIN_SCORE", "0.35"))
else:
    embedder = load_local_embedder()
    METHOD_NAME = info["embedding_method"]
    MIN_CONFIDENCE = info["min_confidence"]

TOPICS = info["topics"]
MAX_QUERY_CHARS = info["max_query_chars"]
print(f"Loaded index: {len(store.chunks)} chunks, method = {METHOD_NAME}")


@app.after_request
def add_cors_headers(response):
    """Allow the React app (a different port = a different 'origin') to call this API."""
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def validate(payload):
    """Return (clean_values, errors). errors maps field -> message a person can understand."""
    if not isinstance(payload, dict):
        return None, {"body": "Send a JSON object like {\"query\": \"...\", \"top_k\": 3}."}
    errors, clean = {}, {}

    query = payload.get("query")
    if not isinstance(query, str) or not query.strip():
        errors["query"] = "Type a question or a few words to search for."
    elif len(query.strip()) > MAX_QUERY_CHARS:
        errors["query"] = f"Query is too long ({len(query.strip())} characters). Use at most {MAX_QUERY_CHARS}."
    else:
        clean["query"] = " ".join(query.split())

    top_k = payload.get("top_k", 3)
    if isinstance(top_k, bool):                       # True/False are ints in Python: reject them explicitly
        errors["top_k"] = f"Must be a whole number from 1 to {MAX_TOP_K}."
    else:
        try:
            number = float(top_k)
            if not number.is_integer() or not 1 <= number <= MAX_TOP_K:
                raise ValueError
            clean["top_k"] = int(number)
        except (TypeError, ValueError):
            errors["top_k"] = f"Must be a whole number from 1 to {MAX_TOP_K}."

    topic = payload.get("topic")
    if topic in (None, "", "All"):
        clean["topic"] = None
    elif topic not in TOPICS:
        errors["topic"] = f"Unknown topic '{topic}'. Choose one of: {', '.join(TOPICS)}."
    else:
        clean["topic"] = topic
    return clean, errors


def query_words(query):
    """Words of the query worth highlighting in the results (no stop words, at least 3 letters)."""
    words = re.findall(r"[A-Za-z0-9]+", query.lower())
    return sorted({w for w in words if w not in se.STOP_WORDS and len(w) >= 3})


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "embedding_method": METHOD_NAME, "n_chunks": len(store.chunks),
                    "n_documents": info["n_documents"]})


@app.get("/api/documents")
def documents():
    return jsonify({"topics": TOPICS, "documents": info["documents"], "max_top_k": MAX_TOP_K,
                    "max_query_chars": MAX_QUERY_CHARS})


@app.route("/api/search", methods=["POST", "OPTIONS"])
def search():
    if request.method == "OPTIONS":           # browser "preflight" check before a POST
        return ("", 204)
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be JSON (Content-Type: application/json)."}), 400

    clean, errors = validate(payload)
    if errors:
        return jsonify({"error": "Some inputs are invalid.", "fields": errors}), 422

    # One result per note (its best section), so a single note cannot fill every place in the top k.
    hits = se.search_best_chunk_per_document(embedder, store, clean["query"], top_k=clean["top_k"],
                                             topic=clean["topic"])
    confidence, unknown = se.match_confidence(embedder, store, clean["query"])
    good_match = confidence >= MIN_CONFIDENCE
    results = [{
        "rank": i + 1,
        "doc_id": chunk["doc_id"],
        "title": chunk["title"],
        "topic": chunk["topic"],
        "heading": chunk["heading"],
        "snippet": se.make_snippet(chunk["text"]),
        "score": round(score, 3),
    } for i, (chunk, score) in enumerate(hits)]

    note = None
    if not good_match:
        note = "No good match: the course notes probably do not cover this question."
        if unknown:
            note += f" These words do not appear in any note: {', '.join(unknown)}."
    return jsonify({
        "query": clean["query"],
        "results": results,
        "confidence": round(confidence, 3),
        "threshold": MIN_CONFIDENCE,
        "good_match": good_match,
        "note": note,
        "highlight_words": query_words(clean["query"]),
        "embedding_method": METHOD_NAME,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
