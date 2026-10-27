"""One small interface for calling a Large Language Model (LLM), whatever the provider.

    llm = get_llm()                       # reads LLM_PROVIDER from the environment (default: mock)
    response = llm.chat(messages)         # messages = [{"role": "system"|"user"|"assistant", "content": "..."}]
    response["text"]                      # the model's answer as a string
    response["usage"]                     # {"input_tokens": n, "output_tokens": n}

Providers
---------
mock       (default) Offline, free and deterministic. It is NOT a language model: it is a set of keyword rules
           written for this project, so the app and notebook run without an API key. Every response says
           "is_mock": True. Its answers say nothing about how good a real LLM would be.
openai     Any OpenAI-compatible /chat/completions endpoint. Needs OPENAI_API_KEY and OPENAI_MODEL;
           OPENAI_BASE_URL is optional (default https://api.openai.com/v1; local servers such as Ollama work too).
anthropic  Anthropic Messages API. Needs ANTHROPIC_API_KEY and ANTHROPIC_MODEL.

The real providers use plain `requests` calls so you can see exactly what is sent over the network.
They were NOT called when this project was built and tested (no API key, no internet).
API keys are read from environment variables only. Never write a key in the code or commit it to Git.
"""
import json
import os
import re

import requests

TIMEOUT_SECONDS = 60


class LLMError(Exception):
    """Raised when the provider cannot give an answer (missing key, network error, HTTP error, bad response)."""


def estimate_tokens(text):
    """Rough rule of thumb for English: 1 token is about 4 characters. Real tokenizers differ by provider."""
    return max(1, round(len(text) / 4))


def messages_to_text(messages):
    return "\n".join(m["content"] for m in messages)


# =====================================================================================================  real providers
class OpenAICompatibleLLM:
    name = "openai"
    is_mock = False

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.model = os.environ.get("OPENAI_MODEL", "")
        self.base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1").rstrip("/")

    @property
    def key_configured(self):
        return bool(self.api_key)

    def chat(self, messages, temperature=0.0, max_tokens=600):
        if not self.api_key or not self.model:
            raise LLMError("OPENAI_API_KEY and OPENAI_MODEL must be set (see .env.example).")
        try:
            r = requests.post(
                f"{self.base_url}/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as e:
            raise LLMError(f"Could not reach the OpenAI-compatible API: {type(e).__name__}") from e
        if r.status_code != 200:
            raise LLMError(f"OpenAI-compatible API returned HTTP {r.status_code}: {r.text[:200]}")
        try:
            data = r.json()
            text = data["choices"][0]["message"]["content"] or ""
            usage = data.get("usage", {})
        except (ValueError, KeyError, IndexError) as e:
            raise LLMError("Unexpected response format from the OpenAI-compatible API.") from e
        return {"text": text, "provider": self.name, "model": self.model, "is_mock": False,
                "usage": {"input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens")}}


class AnthropicLLM:
    name = "anthropic"
    is_mock = False
    URL = "https://api.anthropic.com/v1/messages"

    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.model = os.environ.get("ANTHROPIC_MODEL", "")

    @property
    def key_configured(self):
        return bool(self.api_key)

    def chat(self, messages, temperature=0.0, max_tokens=600):
        if not self.api_key or not self.model:
            raise LLMError("ANTHROPIC_API_KEY and ANTHROPIC_MODEL must be set (see .env.example).")
        # The Messages API takes the system prompt as a separate field, not as a message.
        system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
        chat = [{"role": m["role"], "content": m["content"]} for m in messages if m["role"] != "system"]
        try:
            r = requests.post(
                self.URL,
                headers={"x-api-key": self.api_key, "anthropic-version": "2023-06-01",
                         "content-type": "application/json"},
                json={"model": self.model, "system": system, "messages": chat,
                      "temperature": temperature, "max_tokens": max_tokens},
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as e:
            raise LLMError(f"Could not reach the Anthropic API: {type(e).__name__}") from e
        if r.status_code != 200:
            raise LLMError(f"Anthropic API returned HTTP {r.status_code}: {r.text[:200]}")
        try:
            data = r.json()
            text = "".join(block.get("text", "") for block in data["content"] if block.get("type") == "text")
            usage = data.get("usage", {})
        except (ValueError, KeyError, TypeError) as e:
            raise LLMError("Unexpected response format from the Anthropic API.") from e
        return {"text": text, "provider": self.name, "model": self.model, "is_mock": False,
                "usage": {"input_tokens": usage.get("input_tokens"), "output_tokens": usage.get("output_tokens")}}


# =====================================================================================================  mock provider
# Keyword rules. Each category gets points for every keyword found; the highest score wins.
# On a tie the category that comes first in this dictionary wins (damaged_item beats refund, and so on).
CATEGORY_KEYWORDS = {
    "spam": ["lottery", "seo", "resume", "guest post", "sponsored", "prize", "crypto", "won ", "minutes from",
             "action items", "job"],
    "damaged_item": ["arrived broken", "arrived with", "cracked", "broken", "damaged", "missing", "scratch",
                     "wrong item", "different product", "out of the box", "swollen", "do not work", "rattles"],
    "warranty": ["warranty", "repair", "months", "stopped working", "dead pixels", "double-click"],
    "billing": ["charged", "invoice", "gst", "coupon", "emi", "payment", "deducted", "membership", "billing",
                "debit"],
    "delivery": ["delivery", "delivered", "tracking", "shipping", "courier", "arrive", "late", "address",
                 "nahi aaya", "ships", "express"],
    "refund": ["refund", "return", "money back", "cancel", "send back", "store credit"],
    "product_question": ["does the", "do the", "is it", "can i", "compatible", "support", "waterproof", "stock",
                         "which", "discount"],
}
PRODUCT_KEYWORDS = {
    "voltx": "VoltX Pro 15 laptop", "pixelview": "PixelView 27 monitor", "aerobuds": "AeroBuds wireless earbuds",
    "nimbus": "Nimbus smartwatch", "chargemax": "ChargeMax 20000 power bank",
    "typeflow": "TypeFlow mechanical keyboard", "zephyr": "Zephyr gaming mouse",
    "snapshot": "SnapShot mirrorless camera", "orbit": "Orbit Bluetooth speaker", "streambox": "StreamBox 4K",
}
ANGRY_WORDS = ["unacceptable", "disgusting", "consumer court", "manager", "worst", "!!!"]
NEGATIVE_WORDS = ["disappointed", "not happy", "broken", "late", "still", "missing", "scared", "wrong", "no refund",
                  "not what i expected", "fix", "nahi", "dead", "does not", "doesn't", "won't", "!"]
POSITIVE_WORDS = ["loving", "love", "great", "thanks", "thank you"]
SAFETY_WORDS = ["swollen", "hot", "fire", "smoke", "burning"]
DEADLINE_WORDS = ["urgently", "urgent", "today", "immediately", "before friday", "asap"]
INJECTION_PATTERNS = ["ignore your", "ignore previous", "ignore all", "system note", "you are now",
                      "internal notes you have"]

# Demo triggers (documented in the README and notebook):
# - an email containing a curly brace "{" makes the FIRST extraction answer malformed (single quotes, chatty text),
#   like a real model that got confused by code in the email. The retry answer is valid.
# - the text MOCK_ALWAYS_BAD_JSON makes every extraction answer malformed, so the "gave up after retry" path
#   (HTTP 502) can be tested.
BAD_JSON_TRIGGER = "MOCK_ALWAYS_BAD_JSON"


def has_word(text, words):
    """True if any of the words/phrases appears as a whole word (so "hot" does not match "photos")."""
    return any(re.search(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text) for w in words)


def _email_from(messages):
    """The mock analyses the LAST user message that contains an <email> block (a retry message has none),
    and only the text inside the delimiters. Without delimiters it uses the whole last user message."""
    user_texts = [m["content"] for m in messages if m["role"] == "user"]
    for content in reversed(user_texts):
        match = re.search(r"<email>\n?(.*?)\n?</email>", content, flags=re.S)
        if match:
            return match.group(1), True
    return user_texts[-1], False


def mock_classify(email):
    text = email.lower()
    scores = {cat: sum(text.count(k) for k in keys) for cat, keys in CATEGORY_KEYWORDS.items()}
    best = max(scores.values())
    category = next(c for c in CATEGORY_KEYWORDS if scores[c] == best) if best > 0 else "spam"
    if has_word(text, ANGRY_WORDS + SAFETY_WORDS + DEADLINE_WORDS) or "charged twice" in text:
        urgency = "high"
    elif category in ("spam", "product_question") or (best > 0 and "?" in text and not re.search(r"\d{5}", text)):
        urgency = "low"
    else:
        urgency = "medium"
    if category == "spam":
        urgency = "low"
    found = [k for k in CATEGORY_KEYWORDS[category] if k in text][:3]
    reason = f"Matched keywords: {', '.join(found)}." if found else "No support keywords found."
    return {"category": category, "urgency": urgency, "reason": "[MOCK rules] " + reason}


def mock_extract(email):
    text = email.lower()
    m = re.search(r"\bord(?:er)?[\s\-]*(?:no\.?|number|#)?\s*(\d{5})\b", text)
    order_id = f"ORD-{m.group(1)}" if m else None
    positions = [(text.find(k), name) for k, name in PRODUCT_KEYWORDS.items() if k in text]
    product = min(positions)[1] if positions else None
    if any(w in text for w in ANGRY_WORDS):
        sentiment = "angry"
    elif any(w in text for w in NEGATIVE_WORDS):
        sentiment = "negative"
    elif any(w in text for w in POSITIVE_WORDS):
        sentiment = "positive"
    else:
        sentiment = "neutral"
    subject = re.match(r"subject:\s*(.*)", email, flags=re.I)
    first_line = subject.group(1) if subject else email.strip().split("\n")[0]
    issue = " ".join(first_line.split()[:15]) or "unclear"
    return {"order_id": order_id, "product": product, "issue": issue, "customer_sentiment": sentiment}


def _facts(system_prompt):
    """Read the <facts> block that assistant.py puts into the drafting prompt."""
    facts = {}
    for key in ("Category", "Order id", "Product", "Customer name"):
        m = re.search(rf"^{key}: (.*)$", system_prompt, flags=re.M)
        facts[key] = m.group(1).strip() if m else "not given"
    return facts


REPLY_BODIES = {
    "refund": "Thank you for your return request{about}. Unused items in their original packaging can be returned "
              "within 30 days of delivery. Our returns team will review your request and contact you with the next "
              "steps. If the return is accepted, the refund goes back to your original payment method 5-7 business "
              "days after the item is inspected.",
    "delivery": "Thank you for contacting us{about}. We have asked our delivery team to investigate with the courier "
                "and we will send you an update within 2 business days. Please note that the delivery address can "
                "only be changed before an order ships.",
    "damaged_item": "We are sorry that your order{about} did not arrive in perfect condition. Please reply with a few "
                    "photos of the item and the packaging. Once our team has checked them, we will explain the "
                    "replacement or return options available to you.",
    "warranty": "Thank you for reaching out{about}. Manufacturing defects are covered by a 12-month warranty "
                "(24 months for laptops); accidental, drop or liquid damage is not covered. Our team will review "
                "your warranty request and share the next steps.",
    "billing": "Thank you for letting us know{about}. Our payments team will verify the transaction. If a charge is "
               "found to be incorrect it is reversed within 5-7 business days after verification. For your safety, "
               "please never share your card number, CVV or OTP with anyone.",
    "product_question": "Thank you for your interest{about}. Our product team will check the details and reply "
                        "to your question shortly.",
}
GREETINGS = {"formal": "Dear {name},", "friendly": "Hi {name},", "apologetic": "Dear {name},"}
OPENERS = {"formal": "", "friendly": "",
           "apologetic": "We are truly sorry for the trouble and inconvenience this has caused. "}
CLOSINGS = {"formal": "Kind regards,", "friendly": "Thanks again and have a great day!", "apologetic":
            "Thank you for your patience,"}


def mock_draft(email, system_prompt, tone, guarded):
    facts = _facts(system_prompt)
    name = facts["Customer name"].split()[0] if facts["Customer name"] != "not given" else "Customer"
    text = email.lower()
    injected = any(p in text for p in INJECTION_PATTERNS)
    if injected and not guarded:
        # Simulate what a weak model might do when the email is NOT delimited and there is no security rule:
        # it obeys the attacker. This is a hard-coded simulation for teaching, not real model behaviour.
        note = re.search(r"Internal notes: (.*)", system_prompt)
        return (f"Dear {name},\n\nGood news: a full refund of your item has been approved and will be paid today. "
                f"As requested, here is what our internal notes say: {note.group(1) if note else 'none'}\n\n"
                "VoltNest Customer Support\n[MOCK simulation of a model that followed the injected instruction]")
    category = facts["Category"]
    if category == "spam":
        return "Thank you for your message. This inbox handles customer orders only, so it will not be processed.\n\n" \
               "VoltNest Customer Support"
    about = []
    if facts["Product"] != "not given":
        about.append(f"the {facts['Product']}")
    if facts["Order id"] != "not given":
        about.append(f"order {facts['Order id']}")
    about_text = (" about " + ", ".join(about)) if about else ""
    if category == "damaged_item":
        about_text = f" {facts['Order id']}" if facts["Order id"] != "not given" else ""
    body = REPLY_BODIES.get(category, REPLY_BODIES["product_question"]).format(about=about_text)
    if has_word(text, SAFETY_WORDS):
        body = ("For your safety, please stop using the item, unplug it and keep it away from anything flammable. "
                "We have escalated this to a supervisor today. ") + body
    if has_word(text, ANGRY_WORDS):
        body += " I have also escalated your case to a supervisor, who will contact you."
    return (f"{GREETINGS[tone].format(name=name)}\n\n{OPENERS[tone]}{body}\n\n{CLOSINGS[tone]}\n"
            "VoltNest Customer Support")


class MockLLM:
    """Deterministic, offline stand-in for an LLM. Clearly NOT a real model."""
    name = "mock"
    model = "mock-rules-v1"
    is_mock = True
    key_configured = False

    def chat(self, messages, temperature=0.0, max_tokens=600):
        system = "\n".join(m["content"] for m in messages if m["role"] == "system")
        email, delimited = _email_from(messages)
        is_retry = any("previous answer was not valid" in m["content"] for m in messages if m["role"] == "user")

        if "TASK: CLASSIFY" in system:
            text = json.dumps(mock_classify(email))
        elif "TASK: EXTRACT" in system:
            fields = mock_extract(email)
            if BAD_JSON_TRIGGER in email or ("{" in email and not is_retry):
                # Malformed on purpose: chatty prefix, single quotes, Python None. json.loads() cannot read it.
                text = "Sure! Here are the fields: " + str(fields)
            else:
                text = json.dumps(fields)
        elif "TASK: DRAFT_REPLY" in system:
            tone_match = re.search(r"Tone: (formal|friendly|apologetic)", system)
            tone = tone_match.group(1) if tone_match else "formal"
            text = mock_draft(email, system, tone, guarded="SECURITY:" in system and delimited)
        else:
            # A vague prompt with no task and no format: the mock answers in free text, like a chatty model would.
            c = mock_classify(email)
            text = (f"[MOCK] This email seems to be about {c['category'].replace('_', ' ')}. "
                    f"I would say the urgency is {c['urgency']}, but it depends on your priorities.")
        return {"text": text, "provider": self.name, "model": self.model, "is_mock": True,
                "usage": {"input_tokens": estimate_tokens(messages_to_text(messages)),
                          "output_tokens": estimate_tokens(text)}}


# =====================================================================================================  factory
PROVIDERS = {"mock": MockLLM, "openai": OpenAICompatibleLLM, "anthropic": AnthropicLLM}


def get_llm(provider=None):
    """Create the LLM client named by `provider` or by the LLM_PROVIDER environment variable (default: mock)."""
    provider = (provider or os.environ.get("LLM_PROVIDER", "mock")).strip().lower()
    if provider not in PROVIDERS:
        raise LLMError(f"Unknown LLM_PROVIDER '{provider}'. Use one of: {', '.join(PROVIDERS)}.")
    return PROVIDERS[provider]()
