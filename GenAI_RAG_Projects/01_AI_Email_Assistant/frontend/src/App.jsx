import { useEffect, useState } from "react";
import { getHealth, getSamples, processEmail } from "./api.js";

const TONES = ["formal", "friendly", "apologetic"];
const MAX_CHARS = 5000;

// Friendly labels for the extracted JSON fields.
const FIELD_LABELS = {
  order_id: "Order ID",
  product: "Product",
  issue: "Issue",
  customer_sentiment: "Sentiment",
};

function App() {
  const [health, setHealth] = useState(null);     // which provider the API uses
  const [samples, setSamples] = useState([]);
  const [email, setEmail] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [tone, setTone] = useState("formal");
  const [result, setResult] = useState(null);
  const [reply, setReply] = useState("");         // editable copy of the draft
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  // Load provider info and sample emails once when the page opens.
  useEffect(() => {
    getHealth().then(setHealth).catch((err) => setError(err.message));
    getSamples().then((data) => setSamples(data.samples)).catch(() => {});
  }, []);

  function pickSample(event) {
    const sample = samples.find((s) => s.id === event.target.value);
    if (sample) {
      setEmail(sample.email);
      setCustomerName(sample.customer_name);
      setResult(null);
      setFieldErrors({});
    }
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setFieldErrors({});
    setCopied(false);
    // Simple checks in the browser; the API checks everything again.
    if (!email.trim()) {
      setFieldErrors({ email: "Paste an email first." });
      return;
    }
    if (email.length > MAX_CHARS) {
      setFieldErrors({ email: `Too long: ${email.length} characters (limit ${MAX_CHARS}).` });
      return;
    }
    setLoading(true);
    setResult(null);
    try {
      const data = await processEmail(email, tone, customerName);
      setResult(data);
      setReply(data.draft.reply);
    } catch (err) {
      setError(err.message);
      setFieldErrors(err.fields || {});
    } finally {
      setLoading(false);
    }
  }

  async function copyReply() {
    try {
      await navigator.clipboard.writeText(reply);
      setCopied(true);
    } catch {
      setError("Could not copy automatically. Select the text and copy it by hand.");
    }
  }

  return (
    <main className="page">
      <header>
        <h1>AI Email Assistant</h1>
        <p className="muted">
          Paste a customer email. The assistant suggests a category, pulls out the key details and drafts a reply.
        </p>
      </header>

      {health && health.is_mock && (
        <div className="banner">
          <strong>Mock mode.</strong> Answers come from simple keyword rules running offline, not from a real
          language model. Set <code>LLM_PROVIDER</code> and an API key in <code>.env</code> to use a real model.
        </div>
      )}
      {health && !health.is_mock && (
        <div className="banner real">
          Using provider <strong>{health.provider}</strong> ({health.model}). Each request costs money.
        </div>
      )}

      {error && <div className="alert">{error}</div>}

      <form onSubmit={handleSubmit} className="card" noValidate>
        <div className="row">
          <label>
            Sample email
            <select defaultValue="" onChange={pickSample}>
              <option value="" disabled>
                {samples.length ? "Choose a sample…" : "No samples loaded"}
              </option>
              {samples.map((s) => (
                <option key={s.id} value={s.id}>{s.label}</option>
              ))}
            </select>
          </label>
          <label>
            Customer name (optional)
            <input value={customerName} onChange={(e) => setCustomerName(e.target.value)} maxLength={100} />
          </label>
          <label>
            Reply tone
            <select value={tone} onChange={(e) => setTone(e.target.value)}>
              {TONES.map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            {fieldErrors.tone && <span className="hint error">{fieldErrors.tone}</span>}
          </label>
        </div>

        <label>
          Customer email
          <textarea
            rows={9}
            value={email}
            onChange={(e) => { setEmail(e.target.value); setFieldErrors({}); }}
            className={fieldErrors.email ? "invalid" : ""}
            placeholder="Subject: Where is my order?&#10;&#10;Hi, my order ORD-12345 ..."
          />
          <span className={fieldErrors.email ? "hint error" : "hint"}>
            {fieldErrors.email || `${email.length} / ${MAX_CHARS} characters`}
          </span>
        </label>

        <button type="submit" disabled={loading}>
          {loading ? "Processing…" : "Process email"}
        </button>
      </form>

      {result && (
        <>
          <div className="review">
            Human review required: read and edit the draft before sending. The AI can be wrong.
          </div>

          {result.warnings.map((w) => <div key={w} className="warning">{w}</div>)}

          <div className="results">
            <section className="card">
              <h2>1. Category</h2>
              <span className="badge">{result.classification.category.replace("_", " ")}</span>
              <span className={"badge urgency-" + result.classification.urgency}>
                {result.classification.urgency} urgency
              </span>
              <p className="muted small">{result.classification.reason}</p>
            </section>

            <section className="card">
              <h2>2. Extracted details</h2>
              <table>
                <tbody>
                  {Object.entries(FIELD_LABELS).map(([key, label]) => (
                    <tr key={key}>
                      <th>{label}</th>
                      <td>{result.fields[key] ?? <span className="muted">not found</span>}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          </div>

          <section className="card">
            <h2>3. Draft reply ({tone})</h2>
            <textarea rows={12} value={reply} onChange={(e) => { setReply(e.target.value); setCopied(false); }} />
            <ul className="checks">
              {result.draft.checks.map((c) => (
                <li key={c.check} className={c.passed ? "pass" : "fail"}>
                  {c.passed ? "✓" : "✗"} {c.detail}
                </li>
              ))}
            </ul>
            <button type="button" onClick={copyReply}>{copied ? "Copied" : "Copy reply"}</button>
            <p className="muted small">
              Provider: {result.provider}{result.is_mock ? " (mock)" : ""} · prompt {result.prompt_version} ·
              about {result.usage.input_tokens + result.usage.output_tokens} tokens
            </p>
          </section>
        </>
      )}
    </main>
  );
}

export default App;
