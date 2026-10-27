"""Flask API for the AI Email Assistant.

Run from the project root:
    python backend/app.py                         # mock provider (offline, free) on http://localhost:5000
    LLM_PROVIDER=anthropic python backend/app.py  # a real provider (needs a key, see .env.example)

Endpoints
    GET  /api/health    -> provider name, is it the mock, is an API key configured (yes/no, never the key itself)
    GET  /api/samples   -> a few sample emails from data/customer_emails.csv for the frontend's picker
    POST /api/classify  -> {"email"}                      -> category + urgency
    POST /api/extract   -> {"email"}                      -> order_id, product, issue, customer_sentiment
    POST /api/draft     -> {"email", "tone", ...}         -> draft reply + output checks
    POST /api/process   -> {"email", "tone", ...}         -> all three at once (what the frontend uses)

The LLM client is created ONCE at start-up. Every reply is a DRAFT: a human must review it before sending.
"""
import csv
import os
import sys

from flask import Flask, jsonify, request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import assistant  # noqa: E402
import prompts  # noqa: E402
from llm import LLMError, get_llm  # noqa: E402

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAMPLES_PATH = os.path.join(BASE_DIR, "data", "customer_emails.csv")
MAX_EMAIL_CHARS = 5000

ALLOWED_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")


def load_env_file(path=os.path.join(BASE_DIR, ".env")):
    """Tiny .env reader (KEY=value lines) so you don't need python-dotenv. Real environment variables win."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file()
app = Flask(__name__)
llm = get_llm()          # created once; raises a clear error for an unknown LLM_PROVIDER
print(f"LLM provider: {llm.name} ({'MOCK - offline rules, not a real model' if llm.is_mock else llm.model})")


def load_samples(limit_per_category=2):
    """Pick a few emails per category for the sample picker (internal notes are NOT sent to the browser)."""
    if not os.path.exists(SAMPLES_PATH):
        return []
    picked, counts = [], {}
    with open(SAMPLES_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            cat = row["expected_category"]
            is_special = "ignore your previous instructions" in row["body"] or "UNACCEPTABLE" in row["subject"]
            if counts.get(cat, 0) < limit_per_category or is_special:
                counts[cat] = counts.get(cat, 0) + 1
                picked.append({"id": row["email_id"], "label": f"{cat}: {row['subject']}",
                               "customer_name": row["customer_name"],
                               "email": f"Subject: {row['subject']}\n\n{row['body']}"})
    return picked


SAMPLES = load_samples()


@app.after_request
def add_cors_headers(response):
    """Allow the React app (a different port = a different 'origin') to call this API."""
    response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def validate(payload, need_tone=False):
    """Return (clean, errors). errors maps field -> message a person can understand."""
    if not isinstance(payload, dict):
        return None, {"body": "Send a JSON object like {\"email\": \"...\"}."}
    errors, clean = {}, {}
    email = payload.get("email")
    if not isinstance(email, str) or not email.strip():
        errors["email"] = "Paste the customer's email (it cannot be empty)."
    elif len(email) > MAX_EMAIL_CHARS:
        errors["email"] = f"The email is too long ({len(email)} characters). The limit is {MAX_EMAIL_CHARS}."
    else:
        clean["email"] = email.strip()
    if need_tone:
        tone = payload.get("tone", "formal")
        if tone not in prompts.TONES:
            errors["tone"] = f"Unknown tone '{tone}'. Choose one of: {', '.join(prompts.TONES)}."
        else:
            clean["tone"] = tone
        name = payload.get("customer_name", "")
        if not isinstance(name, str) or len(name) > 100:
            errors["customer_name"] = "Customer name must be text of at most 100 characters."
        else:
            clean["customer_name"] = name.strip()
        note = payload.get("internal_note", "")
        if not isinstance(note, str) or len(note) > 1000:
            errors["internal_note"] = "Internal note must be text of at most 1000 characters."
        else:
            clean["internal_note"] = note.strip()
    return clean, errors


def run(job, need_tone=False):
    """Shared request handling: CORS preflight, JSON check, validation, call the assistant, map errors."""
    if request.method == "OPTIONS":
        return ("", 204)
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "Request body must be JSON (Content-Type: application/json)."}), 400
    clean, errors = validate(payload, need_tone)
    if errors:
        return jsonify({"error": "Some inputs are invalid.", "fields": errors}), 422
    try:
        result = job(clean)
    except LLMError as e:          # provider problem: missing key, network, HTTP error from the provider
        return jsonify({"error": f"The language model provider failed: {e}"}), 502
    except assistant.AssistantError as e:   # the model answered but the answer was unusable
        return jsonify({"error": str(e)}), 502
    result.update({"provider": llm.name, "is_mock": llm.is_mock, "human_review_required": True})
    return jsonify(result)


@app.get("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "provider": llm.name,
        "model": llm.model or "(not set)",
        "is_mock": llm.is_mock,
        "api_key_configured": "yes" if llm.key_configured else "no",
        "prompt_version": prompts.PROMPT_VERSION,
        "tones": prompts.TONES,
        "max_email_chars": MAX_EMAIL_CHARS,
    })


@app.get("/api/samples")
def samples():
    return jsonify({"samples": SAMPLES})


@app.route("/api/classify", methods=["POST", "OPTIONS"])
def classify():
    return run(lambda c: {"classification": assistant.classify(llm, c["email"])})


@app.route("/api/extract", methods=["POST", "OPTIONS"])
def extract():
    return run(lambda c: {"fields": assistant.extract(llm, c["email"])})


@app.route("/api/draft", methods=["POST", "OPTIONS"])
def draft():
    def job(c):
        classification = assistant.classify(llm, c["email"])
        fields = assistant.extract(llm, c["email"])
        result = assistant.draft_reply(llm, c["email"], c["tone"], classification["category"], fields,
                                       c["customer_name"], c["internal_note"])
        return {"draft": result, "tone": c["tone"]}
    return run(job, need_tone=True)


@app.route("/api/process", methods=["POST", "OPTIONS"])
def process():
    return run(lambda c: assistant.process(llm, c["email"], c["tone"], c["customer_name"], c["internal_note"]),
               need_tone=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="127.0.0.1", port=port, debug=os.environ.get("FLASK_DEBUG") == "1")
