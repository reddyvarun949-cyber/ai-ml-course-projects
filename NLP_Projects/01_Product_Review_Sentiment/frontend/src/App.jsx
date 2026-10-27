import { useEffect, useState } from "react";
import { analyzeBatch, analyzeReview, getExamples, getHealth } from "./api.js";

const LABELS = ["negative", "neutral", "positive"];

// ---------------------------------------------------------------------------
// Small display components
// ---------------------------------------------------------------------------

// Coloured pill showing the predicted label.
function LabelBadge({ label }) {
  return <span className={"badge badge-" + label}>{label}</span>;
}

// One horizontal bar per class showing the probability.
function ProbabilityBars({ probabilities }) {
  return (
    <div className="bars">
      {LABELS.map((label) => {
        const percent = Math.round((probabilities[label] || 0) * 100);
        return (
          <div className="bar-row" key={label}>
            <span className="bar-label">{label}</span>
            <div className="bar-track">
              <div className={"bar-fill fill-" + label} style={{ width: percent + "%" }} />
            </div>
            <span className="bar-value">{percent}%</span>
          </div>
        );
      })}
    </div>
  );
}

// Shows the cleaned review word by word. Words that are part of an influential term are highlighted:
// green-ish = pushed TOWARDS the predicted label, red-ish = pushed AWAY from it.
function HighlightedText({ cleanedText, topTerms }) {
  const wordWeight = {};
  for (const t of topTerms) {
    for (const word of t.term.split(" ")) {
      wordWeight[word] = (wordWeight[word] || 0) + t.weight;
    }
  }
  return (
    <p className="highlighted">
      {cleanedText.split(" ").map((word, i) => {
        const w = wordWeight[word];
        let className = "";
        if (w > 0) className = "mark-for";
        if (w < 0) className = "mark-against";
        return (
          <span key={i} className={className} title={w ? "contribution " + w.toFixed(3) : ""}>
            {word}{" "}
          </span>
        );
      })}
    </p>
  );
}

// ---------------------------------------------------------------------------
// Tab 1: analyse one review
// ---------------------------------------------------------------------------
function SingleReview({ examples, maxChars }) {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setResult(null);
    setError("");
    if (text.trim() === "") {
      setError("Please type a review first.");
      return;
    }
    setLoading(true);
    try {
      setResult(await analyzeReview(text));
    } catch (err) {
      // Show the field message from the API if there is one (e.g. "too long").
      setError(err.fields && err.fields.text ? err.fields.text : err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="card">
        <label htmlFor="review">Customer review</label>
        <textarea
          id="review"
          rows={5}
          value={text}
          placeholder="e.g. Great screen but the battery dies fast."
          onChange={(e) => setText(e.target.value)}
          className={error ? "invalid" : ""}
        />
        <div className="row-between">
          <span className={text.length > maxChars ? "hint danger" : "hint"}>
            {text.length} / {maxChars} characters
          </span>
          <button type="submit" disabled={loading}>
            {loading ? "Analysing…" : "Analyze"}
          </button>
        </div>

        {examples.length > 0 && (
          <div className="examples">
            <span className="hint">Try an example:</span>
            {examples.map((ex) => (
              <button type="button" key={ex} className="chip" onClick={() => { setText(ex); setResult(null); setError(""); }}>
                {ex.length > 40 ? ex.slice(0, 40) + "…" : ex}
              </button>
            ))}
          </div>
        )}
        {error && <div className="alert">{error}</div>}
      </form>

      {result && (
        <section className="card">
          <div className="row-between">
            <div>
              <p className="muted small">Predicted sentiment</p>
              <LabelBadge label={result.label} />
            </div>
            <p className="muted small">Confidence {Math.round(result.confidence * 100)}%</p>
          </div>

          {result.low_confidence && (
            <div className="warning">
              Low confidence: the model is not sure about this review. Please check it yourself.
            </div>
          )}
          {result.known_terms === 0 && (
            <div className="warning">The model did not recognise any words in this text, so this is only a guess.</div>
          )}

          <h3>Probabilities</h3>
          <ProbabilityBars probabilities={result.probabilities} />

          <h3>Words that drove the prediction</h3>
          <HighlightedText cleanedText={result.cleaned_text} topTerms={result.top_terms} />
          <ul className="terms">
            {result.top_terms.map((t) => (
              <li key={t.term} className={t.weight >= 0 ? "term-for" : "term-against"}>
                <code>{t.term}</code> {t.weight >= 0 ? "+" : ""}{t.weight.toFixed(3)}
              </li>
            ))}
          </ul>
          <p className="muted small">
            Positive numbers pushed the review towards “{result.label}”, negative numbers pushed it away. Model: {result.model}.
          </p>
        </section>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------
// Tab 2: analyse many reviews (one per line)
// ---------------------------------------------------------------------------
function BatchReviews({ maxBatch }) {
  const [text, setText] = useState("");
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Each non-empty line is one review.
  const lines = text.split("\n").filter((line) => line.trim() !== "");

  async function handleSubmit(event) {
    event.preventDefault();
    setData(null);
    setError("");
    if (lines.length === 0) {
      setError("Paste at least one review (one per line).");
      return;
    }
    if (lines.length > maxBatch) {
      setError(`Too many reviews: ${lines.length}. The limit is ${maxBatch}.`);
      return;
    }
    setLoading(true);
    try {
      setData(await analyzeBatch(lines));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <form onSubmit={handleSubmit} className="card">
        <label htmlFor="batch">Reviews — one per line (up to {maxBatch})</label>
        <textarea
          id="batch"
          rows={8}
          value={text}
          placeholder={"Love it, superb quality!\nNot worth it.\nIt's okay."}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="row-between">
          <span className="hint">{lines.length} review(s)</span>
          <button type="submit" disabled={loading}>
            {loading ? "Analysing…" : "Analyze all"}
          </button>
        </div>
        {error && <div className="alert">{error}</div>}
      </form>

      {data && (
        <section className="card">
          <div className="summary">
            {LABELS.map((label) => (
              <div key={label} className={"summary-box box-" + label}>
                <strong>{data.summary.counts[label]}</strong>
                <span>{label}</span>
              </div>
            ))}
            {data.summary.invalid > 0 && (
              <div className="summary-box box-invalid">
                <strong>{data.summary.invalid}</strong>
                <span>invalid</span>
              </div>
            )}
          </div>
          <table>
            <thead>
              <tr><th>#</th><th>Review</th><th>Sentiment</th><th>Confidence</th><th>Key terms</th></tr>
            </thead>
            <tbody>
              {data.results.map((r) => (
                <tr key={r.row}>
                  <td>{r.row}</td>
                  <td>{r.text}</td>
                  {r.ok ? (
                    <>
                      <td><LabelBadge label={r.label} /></td>
                      <td>{Math.round(r.confidence * 100)}%{r.low_confidence ? " ⚠" : ""}</td>
                      <td>{r.top_terms.map((t) => t.term).join(", ")}</td>
                    </>
                  ) : (
                    <td colSpan={3} className="danger">{r.error}</td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </>
  );
}

// ---------------------------------------------------------------------------
// The page
// ---------------------------------------------------------------------------
function App() {
  const [tab, setTab] = useState("single");
  const [health, setHealth] = useState(null);
  const [examples, setExamples] = useState([]);
  const [startError, setStartError] = useState("");

  // Check the API and load example reviews once when the page opens.
  useEffect(() => {
    getHealth()
      .then((data) => {
        setHealth(data);
        return getExamples();
      })
      .then((data) => setExamples(data.examples))
      .catch((err) => setStartError(err.message));
  }, []);

  return (
    <main className="page">
      <header>
        <h1>Review Sentiment Analyzer</h1>
        <p className="muted">
          Tag product reviews as positive, neutral or negative and see which words drove the decision.
        </p>
        {health && (
          <p className="muted small">
            Model: {health.model} · test macro-F1 {health.test_macro_f1}
          </p>
        )}
      </header>

      {startError && <div className="alert">{startError}</div>}

      <nav className="tabs">
        <button type="button" className={tab === "single" ? "tab active" : "tab"} onClick={() => setTab("single")}>
          One review
        </button>
        <button type="button" className={tab === "batch" ? "tab active" : "tab"} onClick={() => setTab("batch")}>
          Batch
        </button>
      </nav>

      {tab === "single" ? (
        <SingleReview examples={examples} maxChars={health ? health.max_chars : 2000} />
      ) : (
        <BatchReviews maxBatch={health ? health.max_batch : 50} />
      )}
    </main>
  );
}

export default App;
