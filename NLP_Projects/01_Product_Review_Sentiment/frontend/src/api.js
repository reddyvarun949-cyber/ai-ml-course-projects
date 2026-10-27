// All communication with the Flask backend lives in this one file.
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

// Turns any failed request into an Error with a message a person can read.
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(API_URL + path, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
  } catch (networkError) {
    throw new Error("Cannot reach the API. Is the backend running on " + API_URL + "?");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || "Request failed with status " + response.status);
    error.fields = data.fields || {};
    throw error;
  }
  return data;
}

export function getHealth() {
  return request("/api/health");
}

export function getExamples() {
  return request("/api/examples");
}

export function analyzeReview(text) {
  return request("/api/analyze", { method: "POST", body: JSON.stringify({ text }) });
}

export function analyzeBatch(texts) {
  return request("/api/analyze-batch", { method: "POST", body: JSON.stringify({ texts }) });
}
