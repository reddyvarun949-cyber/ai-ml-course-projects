"""Automated tests for the API. Run from the project root:

    python -m unittest discover -s backend -p "test_*.py" -v

They use Flask's built-in test client, so no server needs to be running.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app  # noqa: E402
from text_utils import clean_text  # noqa: E402


class CleanTextTests(unittest.TestCase):
    def test_lowercase_punctuation_and_negation(self):
        self.assertEqual(clean_text("Doesn't WORK!!!"), "does not work")

    def test_emoji_becomes_word(self):
        self.assertIn("emo_pos", clean_text("Love it 😍"))

    def test_missing_value(self):
        self.assertEqual(clean_text(None), "")


class SentimentApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def analyze(self, text):
        return self.client.post("/api/analyze", json={"text": text})

    def test_health(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(sorted(body["labels"]), ["negative", "neutral", "positive"])

    def test_examples(self):
        data = self.client.get("/api/examples").get_json()
        self.assertGreaterEqual(len(data["examples"]), 3)

    def test_valid_analysis(self):
        r = self.analyze("The battery lasts all day. Highly recommend it!")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["label"], "positive")
        self.assertAlmostEqual(sum(body["probabilities"].values()), 1.0, places=3)
        self.assertTrue(len(body["top_terms"]) > 0)
        self.assertIn("term", body["top_terms"][0])
        print("\n  sample analysis:", {k: body[k] for k in ("label", "probabilities", "top_terms")})

    def test_clear_negative(self):
        body = self.analyze("Stopped working after a week. Waste of money.").get_json()
        self.assertEqual(body["label"], "negative")

    def test_nonsense_has_no_known_terms(self):
        body = self.analyze("qwxz zzqv").get_json()
        self.assertEqual(body["known_terms"], 0)

    def test_missing_text(self):
        r = self.client.post("/api/analyze", json={})
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.get_json()["fields"]["text"], "This field is required.")

    def test_empty_text(self):
        r = self.analyze("    ")
        self.assertEqual(r.status_code, 422)
        self.assertIn("empty", r.get_json()["fields"]["text"])

    def test_only_symbols(self):
        r = self.analyze("!!! ???")
        self.assertEqual(r.status_code, 422)

    def test_too_long(self):
        r = self.analyze("good " * 500)
        self.assertEqual(r.status_code, 422)
        self.assertIn("too long", r.get_json()["fields"]["text"])

    def test_not_a_string(self):
        r = self.analyze(12345)
        self.assertEqual(r.status_code, 422)
        self.assertEqual(r.get_json()["fields"]["text"], "Must be text (a string).")

    def test_body_not_json(self):
        r = self.client.post("/api/analyze", data="hello", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_body_is_a_list(self):
        r = self.client.post("/api/analyze", json=["good"])
        self.assertEqual(r.status_code, 422)

    def test_batch(self):
        texts = ["Love it, superb quality!", "Not worth it. Poor quality.", "", "It's okay. Average product."]
        r = self.client.post("/api/analyze-batch", json={"texts": texts})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["summary"]["total"], 4)
        self.assertEqual(body["summary"]["valid"], 3)
        self.assertEqual(body["summary"]["invalid"], 1)
        self.assertFalse(body["results"][2]["ok"])
        self.assertEqual(sum(body["summary"]["counts"].values()), 3)
        print("\n  batch summary:", body["summary"])

    def test_batch_too_many(self):
        r = self.client.post("/api/analyze-batch", json={"texts": ["good"] * 51})
        self.assertEqual(r.status_code, 422)

    def test_batch_not_a_list(self):
        r = self.client.post("/api/analyze-batch", json={"texts": "good"})
        self.assertEqual(r.status_code, 422)

    def test_batch_empty_list(self):
        r = self.client.post("/api/analyze-batch", json={"texts": []})
        self.assertEqual(r.status_code, 422)

    def test_batch_body_not_json(self):
        r = self.client.post("/api/analyze-batch", data="x", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_cors_headers_present(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.headers["Access-Control-Allow-Origin"], "http://localhost:5173")
        self.assertEqual(self.client.options("/api/analyze").status_code, 204)
        self.assertEqual(self.client.options("/api/analyze-batch").status_code, 204)


if __name__ == "__main__":
    unittest.main()
