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
    error.status = response.status;
    throw error;
  }
  return data;
}

export function getHealth() {
  return request("/api/health");
}

export function getSamples() {
  return request("/api/samples");
}

// Classify + extract + draft in one call. Returns { classification, fields, draft, warnings, usage, ... }.
export function processEmail(email, tone, customerName) {
  return request("/api/process", {
    method: "POST",
    body: JSON.stringify({ email, tone, customer_name: customerName }),
  });
}
