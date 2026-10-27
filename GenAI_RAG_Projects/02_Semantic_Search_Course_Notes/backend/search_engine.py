"""Shared semantic-search code, used by BOTH the notebook and the Flask API.

Keeping it in one file guarantees that the notes are chunked, and queries are embedded, in exactly the same way
when we build the index (notebook) and when we search it (API). Using a different chunker or a different
embedding model for queries than for documents is one of the most common bugs in search systems.

The pipeline:   notes (.md)  ->  chunks  ->  vectors (embeddings)  ->  vector store  ->  top-k search

Three "embedding" methods are available, all offline, all scikit-learn:
    keyword : 1/0 bag of words (does the word appear or not?)  - the keyword-search baseline
    tfidf   : TF-IDF word weights                              - weighted keywords
    lsa     : TF-IDF compressed by TruncatedSVD (Latent Semantic Analysis) into a few dense "topic" dimensions.
              Words that appear in similar notes end up close together, so a query can match a chunk
              that uses related words. This is a small, classical stand-in for a neural embedding model.
"""
import glob
import json
import os
import re

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS, CountVectorizer, TfidfVectorizer

# ----------------------------------------------------------------------------------------------------------------
# 1. Loading notes
# ----------------------------------------------------------------------------------------------------------------


def load_notes(notes_dir):
    """Read every .md file in notes_dir. Returns a list of dicts: doc_id, title, topic, text."""
    docs = []
    for path in sorted(glob.glob(os.path.join(notes_dir, "*.md"))):
        with open(path, encoding="utf-8") as f:
            raw = f.read()
        lines = raw.strip().split("\n")
        title = lines[0].lstrip("#").strip()                 # first line: "# Title"
        topic = "General"
        body_lines = []
        for line in lines[1:]:
            if line.startswith("Topic:"):                    # "Topic: Machine Learning"
                topic = line.split(":", 1)[1].strip()
            else:
                body_lines.append(line.rstrip())
        docs.append({"doc_id": os.path.basename(path), "title": title, "topic": topic,
                     "text": "\n".join(body_lines).strip()})
    return docs


# ----------------------------------------------------------------------------------------------------------------
# 2. Chunking: split by headings, then by paragraphs, with a small word overlap
# ----------------------------------------------------------------------------------------------------------------


def split_sections(text):
    """Split Markdown text at '## ' and '### ' headings. Returns [(heading, section_text), ...]."""
    sections, heading, current = [], "Introduction", []
    for line in text.split("\n"):
        match = re.match(r"^#{2,3}\s+(.*)", line)
        if match:
            if "\n".join(current).strip():
                sections.append((heading, "\n".join(current).strip()))
            heading, current = match.group(1).strip(), []
        else:
            current.append(line)
    if "\n".join(current).strip():
        sections.append((heading, "\n".join(current).strip()))
    return sections


def paragraphs_of(section_text):
    """Paragraphs are separated by blank lines. Lines inside a paragraph are joined with spaces."""
    paras = re.split(r"\n\s*\n", section_text)
    return [" ".join(p.split()) for p in paras if p.strip()]


def chunk_document(doc, max_words=120, overlap_words=25):
    """Turn one note into chunks.

    - Every heading starts a new chunk, so a chunk never mixes two sections.
    - Paragraphs of the same section are packed together until max_words is reached.
    - A single section longer than max_words is cut into word windows that OVERLAP by overlap_words,
      so a sentence cut at the boundary still appears complete in one of the two chunks.
    """
    chunks = []
    for heading, section_text in split_sections(doc["text"]):
        words = " ".join(paragraphs_of(section_text)).split()
        if len(words) <= max_words:
            pieces = [words]
        else:
            step = max_words - overlap_words
            pieces = [words[start:start + max_words] for start in range(0, len(words) - overlap_words, step)]
        for piece in pieces:
            chunks.append({
                "chunk_id": f"{doc['doc_id']}#{len(chunks)}",
                "doc_id": doc["doc_id"],
                "title": doc["title"],
                "topic": doc["topic"],
                "heading": heading,
                "text": " ".join(piece),
            })
    return chunks


def chunk_all(docs, max_words=120, overlap_words=25):
    out = []
    for doc in docs:
        out.extend(chunk_document(doc, max_words, overlap_words))
    return out


def text_for_embedding(chunk):
    """What we actually embed: title + heading + text. The title and heading add useful context words."""
    return f"{chunk['title']}. {chunk['heading']}. {chunk['text']}"


# ----------------------------------------------------------------------------------------------------------------
# 3. Tokens: lowercase words with a tiny suffix-stripping "stemmer"
# ----------------------------------------------------------------------------------------------------------------

STOP_WORDS = set(ENGLISH_STOP_WORDS) | {"use", "used", "using", "like", "make", "way", "does", "doe", "want"}


def simple_stem(word):
    """Very small stemmer: memorising / memorises / memorised -> memoris. Good enough for this course."""
    for suffix in ("ising", "izing", "ised", "ized", "ises", "izes", "ise", "ize",
                   "ings", "ing", "ies", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)] + ("y" if suffix == "ies" else "")
    return word


def tokenize(text):
    """Lowercase, keep letters/digits, drop stop words, stem. Used for documents AND queries."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [simple_stem(w) for w in words if w not in STOP_WORDS and len(w) > 1]


# ----------------------------------------------------------------------------------------------------------------
# 4. Embedding models (all have .fit(texts) and .encode(texts) -> L2-normalised numpy matrix)
# ----------------------------------------------------------------------------------------------------------------


def l2_normalise(matrix):
    """Divide every row by its length so that a dot product equals cosine similarity.
    Rows of all zeros (a query with no known words) stay zero instead of dividing by zero."""
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.where(norms == 0, 1, norms)


class KeywordEmbedder:
    """Baseline: 1 if the (stemmed) word appears, else 0. Only exact word matches can score."""
    name = "keyword"

    def __init__(self, vectorizer=None):
        self.vectorizer = vectorizer or CountVectorizer(tokenizer=tokenize, lowercase=False, binary=True,
                                                        token_pattern=None)

    def fit(self, texts):
        self.vectorizer.fit(texts)
        return self

    def encode(self, texts):
        return l2_normalise(self.vectorizer.transform(texts).toarray().astype(float))


class TfidfEmbedder:
    """TF-IDF: words that are frequent in a chunk but rare in the collection get high weights."""
    name = "tfidf"

    def __init__(self, vectorizer=None):
        self.vectorizer = vectorizer or TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None,
                                                        sublinear_tf=True, min_df=1)

    def fit(self, texts):
        self.vectorizer.fit(texts)
        return self

    def encode(self, texts):
        return l2_normalise(self.vectorizer.transform(texts).toarray())


class LsaEmbedder:
    """LSA = TF-IDF followed by TruncatedSVD. Compresses thousands of word columns into n_components dense
    dimensions. Words that keep appearing in the same chunks share dimensions, so related words can match."""
    name = "lsa"

    def __init__(self, n_components=100, random_state=42, vectorizer=None, svd=None):
        self.vectorizer = vectorizer or TfidfVectorizer(tokenizer=tokenize, lowercase=False, token_pattern=None,
                                                        sublinear_tf=True, min_df=1)
        self.svd = svd or TruncatedSVD(n_components=n_components, random_state=random_state)

    def fit(self, texts):
        tfidf = self.vectorizer.fit_transform(texts)
        self.svd.fit(tfidf)
        return self

    def encode(self, texts):
        return l2_normalise(self.svd.transform(self.vectorizer.transform(texts)))


class SentenceTransformerEmbedder:
    """Optional neural embedding model (pip install sentence-transformers; downloads the model on first use).
    Not installed in the build environment, so this class is documented but NOT tested here."""
    name = "sentence-transformers"

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer   # imported lazily: optional dependency
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def fit(self, texts):          # pre-trained: nothing to learn from our notes
        return self

    def encode(self, texts):
        return np.asarray(self.model.encode(list(texts), normalize_embeddings=True))


# ----------------------------------------------------------------------------------------------------------------
# 5. A tiny vector store: a numpy matrix + a list of chunk metadata
# ----------------------------------------------------------------------------------------------------------------


class VectorStore:
    def __init__(self, embeddings, chunks):
        assert len(embeddings) == len(chunks), "one vector per chunk"
        self.embeddings = np.asarray(embeddings, dtype=np.float32)
        self.chunks = chunks

    def search(self, query_vector, top_k=3, topic=None):
        """Cosine similarity = dot product (all vectors are normalised). Returns [(chunk, score), ...] best first."""
        scores = self.embeddings @ np.asarray(query_vector, dtype=np.float32)
        if topic:
            allowed = np.array([c["topic"] == topic for c in self.chunks])
            scores = np.where(allowed, scores, -np.inf)
        order = np.argsort(-scores)[:top_k]
        return [(self.chunks[i], float(scores[i])) for i in order if np.isfinite(scores[i])]

    def save(self, embeddings_path, chunks_path):
        np.save(embeddings_path, self.embeddings)
        with open(chunks_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=1, ensure_ascii=False)

    @classmethod
    def load(cls, embeddings_path, chunks_path):
        with open(chunks_path, encoding="utf-8") as f:
            chunks = json.load(f)
        return cls(np.load(embeddings_path), chunks)


def search_documents(embedder, store, query, top_k=3, topic=None):
    """Embed the query with the SAME embedder as the chunks, then search the store."""
    query_vector = embedder.encode([query])[0]
    return store.search(query_vector, top_k=top_k, topic=topic)


def search_best_chunk_per_document(embedder, store, query, top_k=3, topic=None):
    """Like search_documents, but at most ONE chunk (the best one) per note.

    Without this, a note with several similar sections can fill all top-k places and hide other relevant notes.
    The API uses this so the student sees k different notes, each with its best-matching section."""
    hits = search_documents(embedder, store, query, top_k=len(store.chunks), topic=topic)
    seen, best = set(), []
    for chunk, score in hits:
        if chunk["doc_id"] not in seen:
            seen.add(chunk["doc_id"])
            best.append((chunk, score))
        if len(best) == top_k:
            break
    return best


def rank_documents(embedder, store, query, top_k=3):
    """Document-level ranking (used for evaluation): each note gets the score of its best chunk."""
    return [(chunk["doc_id"], score) for chunk, score in search_best_chunk_per_document(embedder, store, query, top_k)]


def make_snippet(text, max_chars=260):
    """Shorten text at a word boundary for display."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + " …"


# ----------------------------------------------------------------------------------------------------------------
# 6. "Is this a good match at all?"  Cosine score x share of query words the index knows
# ----------------------------------------------------------------------------------------------------------------


def query_coverage(embedder, query):
    """Share of the query's words that appear in the index vocabulary, plus the unknown words.

    Why: LSA always returns SOME nearest chunk, even for 'cheapest flights to goa'. If most query words were never
    seen in the notes, the high cosine score comes from one or two words only and should not be trusted.
    For a neural model (no vocabulary) we return coverage 1.0."""
    vectorizer = getattr(embedder, "vectorizer", None)
    tokens = tokenize(query)
    if vectorizer is None or not tokens:
        return (1.0 if vectorizer is None else 0.0), []
    vocab = vectorizer.vocabulary_
    unknown = [t for t in tokens if t not in vocab]
    return 1 - len(unknown) / len(tokens), unknown


def match_confidence(embedder, store, query):
    """Confidence that the notes contain an answer = best cosine score x word coverage (0 to 1)."""
    hits = search_documents(embedder, store, query, top_k=1)
    best = hits[0][1] if hits else 0.0
    coverage, unknown = query_coverage(embedder, query)
    return max(best, 0.0) * coverage, unknown
