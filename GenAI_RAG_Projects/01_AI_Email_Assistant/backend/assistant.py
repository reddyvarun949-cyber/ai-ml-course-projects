"""The three jobs of the email assistant, built on top of prompts.py (what we send) and llm.py (who we send it to).

    classify(llm, email)                      -> {"category", "urgency", "reason"}
    extract(llm, email)                       -> {"order_id", "product", "issue", "customer_sentiment"}
    draft_reply(llm, email, tone, ...)        -> {"reply", "checks", "needs_attention"}
    process(llm, email, tone, ...)            -> all three, plus token usage

Why so much checking? An LLM returns TEXT. Even when we ask for JSON it can add extra words, use the wrong quotes,
invent a category or write something we never want to send. So we:
    1. parse the text as JSON          (json.loads)
    2. validate the values             (allowed categories, order-id pattern, ...)
    3. retry ONCE with the error message if it failed, then give up with a clear error
    4. run output checks on the reply  (no refund promises, no internal notes, no card/OTP requests, sign-off)
A human support agent always reviews the draft before it is sent.
"""
import json
import re

import prompts
from llm import LLMError


class AssistantError(Exception):
    """The model answered, but even after one retry the answer was not usable."""


def parse_json(text):
    """Turn the model's text into a dict. Accepts a JSON object wrapped in a ```json code fence
    (models often do that) but nothing else. Raises ValueError with a readable message."""
    cleaned = text.strip()
    fence = re.match(r"^```(?:json)?\s*(.*?)\s*```$", cleaned, flags=re.S)
    if fence:
        cleaned = fence.group(1)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"not valid JSON ({e.msg} at character {e.pos})") from None
    if not isinstance(data, dict):
        raise ValueError("expected a JSON object { ... }")
    return data


def validate_classification(data):
    if data.get("category") not in prompts.CATEGORIES:
        raise ValueError(f"category must be one of {prompts.CATEGORIES}")
    if data.get("urgency") not in prompts.URGENCIES:
        raise ValueError(f"urgency must be one of {prompts.URGENCIES}")
    return {"category": data["category"], "urgency": data["urgency"], "reason": str(data.get("reason", ""))[:200]}


ORDER_ID_PATTERN = re.compile(r"^ORD-\d{5}$")


def validate_fields(data):
    missing = [k for k in ("order_id", "product", "issue", "customer_sentiment") if k not in data]
    if missing:
        raise ValueError(f"missing keys: {', '.join(missing)}")
    order_id = data["order_id"]
    if order_id in ("", "null", "None"):
        order_id = None
    if order_id is not None and not ORDER_ID_PATTERN.match(str(order_id)):
        raise ValueError("order_id must look like ORD-12345 or be null")
    product = data["product"] if data["product"] in prompts.PRODUCTS else None   # unknown product -> null
    if data["customer_sentiment"] not in prompts.SENTIMENTS:
        raise ValueError(f"customer_sentiment must be one of {prompts.SENTIMENTS}")
    return {"order_id": order_id, "product": product, "issue": str(data["issue"] or "")[:200],
            "customer_sentiment": data["customer_sentiment"]}


def _add_usage(total, response):
    for key in ("input_tokens", "output_tokens"):
        total[key] = total.get(key, 0) + (response["usage"].get(key) or 0)


def ask_for_json(llm, messages, validator, usage=None, log=None):
    """Call the model, parse + validate the JSON; on failure retry ONCE with the error message added.
    `log` (a list) collects what happened, so the notebook can show the retry."""
    usage = usage if usage is not None else {}
    log = log if log is not None else []
    for attempt in (1, 2):
        response = llm.chat(messages)
        _add_usage(usage, response)
        try:
            result = validator(parse_json(response["text"]))
            log.append({"attempt": attempt, "ok": True, "raw": response["text"]})
            return result
        except ValueError as e:
            log.append({"attempt": attempt, "ok": False, "raw": response["text"], "error": str(e)})
            messages = messages + [{"role": "assistant", "content": response["text"]}, prompts.retry_message(str(e))]
    raise AssistantError(f"The model did not return valid JSON after a retry: {log[-1]['error']}")


def classify(llm, email, style="few_shot", usage=None, log=None):
    return ask_for_json(llm, prompts.classify_messages(email, style), validate_classification, usage, log)


def extract(llm, email, usage=None, log=None):
    return ask_for_json(llm, prompts.extract_messages(email), validate_fields, usage, log)


# ---------------------------------------------------------------------------------------------- output checks
REFUND_PROMISE = re.compile(
    r"(refund|replacement|compensation)[^.]{0,40}\b(has been|is|was)\s+(approved|confirmed|processed|guaranteed)"
    r"|\b(we will|we'll|i will|i'll)\s+(refund|give you a refund|send you a full refund)"
    r"|\b(approved|confirmed|guarantee)[^.]{0,20}\brefund", flags=re.I)
SENSITIVE_REQUEST = re.compile(r"\b(cvv|otp|password|full card number)\b", flags=re.I)
SAFE_SENSITIVE = re.compile(r"never (share|ask)", flags=re.I)


def check_reply(reply, internal_note=""):
    """Rule-based checks on a drafted reply. Returns a list of {"check", "passed", "detail"}.
    These checks are a safety net, not a guarantee: a human still reviews every reply."""
    checks = []
    m = REFUND_PROMISE.search(reply)
    checks.append({"check": "no_refund_promise", "passed": m is None,
                   "detail": f"Promise found: '{m.group(0)}'" if m else "No refund/replacement promise found."})
    leaked = False
    if internal_note.strip():
        # Leak = any run of 5 consecutive words from the internal note appears in the reply.
        words = re.findall(r"\w+", internal_note.lower())
        reply_words = " ".join(re.findall(r"\w+", reply.lower()))
        leaked = any(" ".join(words[i:i + 5]) in reply_words for i in range(max(1, len(words) - 4)))
    checks.append({"check": "no_internal_note_leak", "passed": not leaked,
                   "detail": "Internal note text appears in the reply!" if leaked else "No internal note text found."})
    asks = [s for s in re.split(r"(?<=[.!?])\s+", reply) if SENSITIVE_REQUEST.search(s) and not SAFE_SENSITIVE.search(s)]
    checks.append({"check": "no_sensitive_data_request", "passed": not asks,
                   "detail": f"Asks for sensitive data: '{asks[0]}'" if asks else "Does not ask for card/OTP/password."})
    checks.append({"check": "has_sign_off", "passed": "VoltNest Customer Support" in reply,
                   "detail": "Signed as VoltNest Customer Support." if "VoltNest Customer Support" in reply
                   else "Missing the sign-off 'VoltNest Customer Support'."})
    n_words = len(reply.split())
    checks.append({"check": "length_ok", "passed": n_words <= 180, "detail": f"{n_words} words (limit 180)."})
    return checks


def looks_like_injection(email):
    """Simple flag for staff: does the email try to give the AI instructions? (keyword heuristic)"""
    patterns = r"ignore (your|all|previous|the above)|system (note|prompt|message)|you are now|disregard .{0,20}instructions"
    return re.search(patterns, email, flags=re.I) is not None


def draft_reply(llm, email, tone, category, fields, customer_name="", internal_note="", usage=None, guarded=True):
    usage = usage if usage is not None else {}
    messages = prompts.draft_messages(email, tone, category, fields, customer_name, internal_note, guarded=guarded)
    response = llm.chat(messages)
    _add_usage(usage, response)
    reply = response["text"].strip()
    checks = check_reply(reply, internal_note)
    failed = [c["check"] for c in checks if not c["passed"]]
    return {"reply": reply, "checks": checks, "needs_attention": bool(failed), "failed_checks": failed}


def process(llm, email, tone="formal", customer_name="", internal_note=""):
    """Run classify -> extract -> draft for one email. Raises LLMError (provider problem) or AssistantError."""
    usage = {}
    classification = classify(llm, email, usage=usage)
    fields = extract(llm, email, usage=usage)
    draft = draft_reply(llm, email, tone, classification["category"], fields, customer_name, internal_note, usage)
    warnings = []
    if looks_like_injection(email):
        warnings.append("This email contains text that tries to give instructions to the AI (possible prompt "
                        "injection). Read it carefully yourself.")
    if classification["urgency"] == "high":
        warnings.append("High urgency: consider escalating to a supervisor.")
    if draft["needs_attention"]:
        warnings.append("The draft failed these checks: " + ", ".join(draft["failed_checks"]) + ". Edit it before sending.")
    return {"classification": classification, "fields": fields, "draft": draft, "warnings": warnings,
            "usage": usage, "provider": llm.name, "model": llm.model, "is_mock": llm.is_mock,
            "prompt_version": prompts.PROMPT_VERSION, "human_review_required": True}


__all__ = ["classify", "extract", "draft_reply", "process", "check_reply", "parse_json", "AssistantError",
           "LLMError", "looks_like_injection"]
