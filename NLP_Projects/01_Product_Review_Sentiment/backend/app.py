"""Flask API for the Product Review Sentiment project.

Run from the project root:
    python backend/app.py
The API starts on http://localhost:5000

Endpoints
    GET  /api/health         -> is the API up and is the model loaded?
    GET  /api/examples       -> a few sample reviews (the frontend shows them as buttons)
    POST /api/analyze        -> {"text": "..."} -> label, probabilities and the words that drove the prediction
    POST /api/analyze-batch  -> {"texts": ["...", "..."]} (up to 50) -> one result per text + a summary count

The model is trained in notebook/Product_Review_Sentiment.ipynb and loaded ONCE when the server starts.
We never retrain on a request.
"""
import json
import os
import sys

import joblib
from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_model.joblib")
INFO_PATH = os.path.join(BASE_DIR, "models", "sentiment_info.json")

# The saved pipeline refers to text_utils.clean_text, so Python must be able to import text_utils (it is in backend/).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from text_utils import clean_text  # noqa: E402

# Which website may call this API from a browser (the Vite dev server by default).
ALLOWED_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

app = Flask(__name__)

# ---- load the model once at start-up ----
if not os.path.exists(MODEL_PATH) or not os.path.exists(INFO_PATH):
    raise SystemExit("Model files not found. Run notebook/Product_Review_Sentiment.ipynb first to create models/.")
model = joblib.load(MODEL_PATH)
with open(INFO_PATH, encoding="utf-8") as f:
    info = json.load(f)

vectorizer = model.named_steps["tfidf"]
classifier = model.named_steps["clf"]
TERMS = vectorizer.get_feature_names_out()
CLASSES = list(classifier.classes_)
MAX_CHARS = info["max_chars"]
MAX_BATCH = info["max_batch"]
LOW_CONFIDENCE = info["low_confidence_below"]


@app.after_request
def add_cors_headers(response):
    """Allow the React app (a different port = a different 'origin') to call this API."""
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def validate_text(value):
    """Return an error message for a bad review text, or None if it is fine."""
    if value is None:
        return "This field is required."
    if not isinstance(value, str):
        return "Must be text (a string)."
    if value.strip() == "":
        return "The review is empty. Type a few words."
    if len(value) > MAX_CHARS:
        return f"The review is too long ({len(value)} characters). The limit is {MAX_CHARS}."
    if clean_text(value) == "":
        return "The review has no letters or numbers the model can read."
    return None


def analyze_texts(texts, top_n=6):
    """Run the model on a list of valid texts and explain each prediction.

    The contribution of a term = its TF-IDF value in this review x the model's weight for that term and the
    predicted class. Positive contribution = pushed towards the predicted label, negative = pushed away from it.
    """
    probabilities = model.predict_proba(texts)          # one row per text, columns in CLASSES order
    matrix = vectorizer.transform(texts)                # the TF-IDF numbers the model saw
    results = []
    for i, text in enumerate(texts):
        probs = {label: round(float(p), 4) for label, p in zip(CLASSES, probabilities[i])}
        label = max(probs, key=probs.get)
        weights = classifier.coef_[CLASSES.index(label)]
        row = matrix.getrow(i)
        contributions = [
            {"term": str(TERMS[j]), "weight": round(float(value * weights[j]), 4)}
            for j, value in zip(row.indices, row.data)
        ]
        contributions.sort(key=lambda c: -abs(c["weight"]))
        confidence = probs[label]
        results.append({
            "label": label,
            "confidence": confidence,
            "low_confidence": confidence < LOW_CONFIDENCE,
            "probabilities": probs,
            "top_terms": contributions[:top_n],
            "known_terms": len(contributions),     # 0 = the model recognised no words at all
            "cleaned_text": clean_text(text),
        })
    return results


def read_json():
    """Return the parsed JSON body, or None if the body is not valid JSON."""
    return request.get_json(silent=True)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "model": info["model_name"],
        "labels": CLASSES,
        "test_macro_f1": info["test_metrics"]["macro_f1"],
        "max_chars": MAX_CHARS,
        "max_batch": MAX_BATCH,
    })


@app.get("/api/examples")
def examples():
    return jsonify({"examples": info["examples"]})


@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":           # browser "preflight" check before a POST
        return ("", 204)
    payload = read_json()
    if payload is None:
        return jsonify({"error": "Request body must be JSON (Content-Type: application/json)."}), 400
    if not isinstance(payload, dict):
        return jsonify({"error": "Send a JSON object like {\"text\": \"...\"}.", "fields": {"body": "Must be an object."}}), 422

    problem = validate_text(payload.get("text"))
    if problem:
        return jsonify({"error": "The review text is invalid.", "fields": {"text": problem}}), 422

    result = analyze_texts([payload["text"]])[0]
    result["model"] = info["model_name"]
    return jsonify(result)


@app.route("/api/analyze-batch", methods=["POST", "OPTIONS"])
def analyze_batch():
    if request.method == "OPTIONS":
        return ("", 204)
    payload = read_json()
    if payload is None:
        return jsonify({"error": "Request body must be JSON (Content-Type: application/json)."}), 400

    # Accept {"texts": [...]} or a plain list [...]
    texts = payload.get("texts") if isinstance(payload, dict) else payload
    if not isinstance(texts, list):
        return jsonify({"error": "Send {\"texts\": [ ... ]} with a list of reviews.",
                        "fields": {"texts": "Must be a list of strings."}}), 422
    if len(texts) == 0:
        return jsonify({"error": "The list of reviews is empty.", "fields": {"texts": "Add at least one review."}}), 422
    if len(texts) > MAX_BATCH:
        return jsonify({"error": f"Too many reviews: {len(texts)}. The limit is {MAX_BATCH} per request.",
                        "fields": {"texts": f"At most {MAX_BATCH} reviews."}}), 422

    # Validate every text; analyse the good ones in ONE model call, report errors per row.
    results = [None] * len(texts)
    good_texts, good_positions = [], []
    for i, text in enumerate(texts):
        problem = validate_text(text)
        if problem:
            results[i] = {"row": i + 1, "ok": False, "text": text if isinstance(text, str) else None, "error": problem}
        else:
            good_texts.append(text)
            good_positions.append(i)
    if good_texts:
        for i, analysis in zip(good_positions, analyze_texts(good_texts, top_n=3)):
            results[i] = {"row": i + 1, "ok": True, "text": texts[i], **analysis}

    counts = {label: 0 for label in CLASSES}
    for r in results:
        if r["ok"]:
            counts[r["label"]] += 1
    return jsonify({
        "results": results,
        "summary": {"total": len(texts), "valid": len(good_texts), "invalid": len(texts) - len(good_texts),
                    "counts": counts},
        "model": info["model_name"],
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
