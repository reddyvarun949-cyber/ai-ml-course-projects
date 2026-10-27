"""Text cleaning shared by the notebook AND the API.

Why a separate file? The model must see text cleaned in exactly the same way during training (notebook) and during
prediction (Flask API). If the two used different cleaning code, predictions would silently get worse.
The notebook imports `clean_text` from here, and the saved pipeline stores a reference to `text_utils.clean_text`,
so the API must be able to `import text_utils` (it lives next to app.py).

Example:
    >>> clean_text("NOT worth it!!! Battery dies sooo fast 😡")
    'not worth it battery dies soo fast emo_neg'
"""
import re

# A few common emojis carry strong sentiment, so we turn them into words instead of throwing them away.
EMOJI_WORDS = {
    "😍": " emo_pos ", "👍": " emo_pos ", "😊": " emo_pos ", "❤️": " emo_pos ", "❤": " emo_pos ", "🔥": " emo_pos ",
    "😡": " emo_neg ", "👎": " emo_neg ", "😞": " emo_neg ", "🤬": " emo_neg ", "💔": " emo_neg ", "🙄": " emo_eyeroll ",
    "😐": " emo_neutral ", "🤷": " emo_neutral ", "🙂": " emo_neutral ",
}

# Expand short forms so that "doesn't", "does not" and "dont" all contain the word "not".
CONTRACTIONS = [
    (r"\bcan't\b|\bcannot\b|\bcant\b", "can not"),
    (r"\bwon't\b|\bwont\b", "will not"),
    (r"n't\b", " not"),
    (r"\b(dont|doesnt|didnt|isnt|wasnt|wouldnt|shouldnt|couldnt|havent|hasnt)\b", lambda m: m.group(1)[:-2] + " not"),
    (r"'s\b", ""),            # "it's" -> "it", "product's" -> "product"
    (r"'re\b|'ve\b|'ll\b|'d\b|'m\b", ""),
]


def clean_text(text):
    """Turn a raw review into lower-case words separated by single spaces.

    Steps: handle missing values -> lower case -> emojis to words -> expand "n't" -> squash letters repeated 3+ times
    ("sooo" -> "soo") -> keep only letters, digits and underscores -> collapse spaces.
    We deliberately KEEP stop words such as "not", "no" and "but": they change the meaning of a review.
    """
    if text is None or not isinstance(text, str):
        return ""
    text = text.lower().replace("’", "'")
    for emoji, word in EMOJI_WORDS.items():
        text = text.replace(emoji, word)
    for pattern, repl in CONTRACTIONS:
        text = re.sub(pattern, repl, text)
    text = re.sub(r"(.)\1{2,}", r"\1\1", text)         # "goooood" -> "good", "!!!!" -> "!!"
    text = re.sub(r"[^a-z0-9_\s]", " ", text)          # drop punctuation and any other symbols
    return re.sub(r"\s+", " ", text).strip()
