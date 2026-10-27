"""Automated tests for the search API. Run from the project root:

    python -m unittest discover -s backend -p "test_*.py" -v

They use Flask's built-in test client, so no server needs to be running.
They test the default offline index (LSA); the optional sentence-transformers backend is not tested.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import app  # noqa: E402

import search_engine as se  # noqa: E402

QUERY = "how do I stop my model memorising the training data"


class SearchApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def post(self, payload):
        return self.client.post("/api/search", json=payload)

    # ---- happy paths ----
    def test_health_reports_method_and_chunks(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(body["status"], "ok")
        self.assertIn(body["embedding_method"], ("lsa", "tfidf", "keyword"))
        self.assertGreater(body["n_chunks"], 20)
        print("\n  health:", body)

    def test_documents_lists_titles_and_topics(self):
        body = self.client.get("/api/documents").get_json()
        self.assertEqual(len(body["documents"]), 20)
        self.assertIn("Machine Learning", body["topics"])
        self.assertTrue(all({"doc_id", "title", "topic"} <= set(d) for d in body["documents"]))

    def test_meaning_search_finds_overfitting_note(self):
        r = self.post({"query": QUERY, "top_k": 3})
        self.assertEqual(r.status_code, 200)
        body = r.get_json()
        self.assertEqual(len(body["results"]), 3)
        titles = [res["title"] for res in body["results"]]
        self.assertIn("Overfitting and Regularisation", titles)
        self.assertTrue(body["good_match"])
        first = body["results"][0]
        self.assertTrue({"title", "heading", "snippet", "score", "topic", "rank"} <= set(first))
        scores = [res["score"] for res in body["results"]]
        self.assertEqual(scores, sorted(scores, reverse=True))      # best first
        self.assertEqual(len({res["doc_id"] for res in body["results"]}), 3)   # one result per note
        print("\n  top result:", first["title"], "|", first["heading"], "|", first["score"])

    def test_default_top_k_is_3(self):
        body = self.post({"query": "precision and recall"}).get_json()
        self.assertEqual(len(body["results"]), 3)

    def test_top_k_sent_as_text_is_accepted(self):
        r = self.post({"query": "precision and recall", "top_k": "5"})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.get_json()["results"]), 5)

    def test_topic_filter(self):
        body = self.post({"query": QUERY, "top_k": 5, "topic": "Deep Learning"}).get_json()
        self.assertTrue(body["results"])
        self.assertTrue(all(res["topic"] == "Deep Learning" for res in body["results"]))
        self.assertLessEqual(len(body["results"]), 2)    # only 2 Deep Learning notes, one result each

    def test_topic_all_means_no_filter(self):
        r = self.post({"query": QUERY, "topic": "All"})
        self.assertEqual(r.status_code, 200)

    def test_off_topic_query_is_flagged(self):
        body = self.post({"query": "cheapest flights from mumbai to goa"}).get_json()
        self.assertFalse(body["good_match"])
        self.assertIn("No good match", body["note"])
        self.assertLess(body["confidence"], body["threshold"])

    def test_query_with_no_known_words(self):
        r = self.post({"query": "who won the football world cup"})
        self.assertEqual(r.status_code, 200)
        self.assertFalse(r.get_json()["good_match"])

    def test_highlight_words_skip_stop_words(self):
        body = self.post({"query": QUERY}).get_json()
        self.assertIn("memorising", body["highlight_words"])
        self.assertNotIn("the", body["highlight_words"])

    def test_api_matches_shared_search_code(self):
        # Results from the API must equal a direct call to the shared search module.
        import app as app_module
        direct = se.search_best_chunk_per_document(app_module.embedder, app_module.store, QUERY, top_k=3)
        body = self.post({"query": QUERY, "top_k": 3}).get_json()
        self.assertEqual([c["heading"] for c, _ in direct], [r["heading"] for r in body["results"]])

    # ---- validation errors ----
    def test_empty_query(self):
        for q in ["", "   ", None]:
            r = self.post({"query": q})
            self.assertEqual(r.status_code, 422)
            self.assertIn("query", r.get_json()["fields"])

    def test_query_not_a_string(self):
        r = self.post({"query": 123})
        self.assertEqual(r.status_code, 422)

    def test_query_too_long(self):
        r = self.post({"query": "overfitting " * 100})
        self.assertEqual(r.status_code, 422)
        self.assertIn("too long", r.get_json()["fields"]["query"])

    def test_bad_top_k(self):
        for bad in [0, 11, 2.5, "three", True, -1]:
            r = self.post({"query": QUERY, "top_k": bad})
            self.assertEqual(r.status_code, 422, msg=f"top_k={bad!r}")
            self.assertIn("top_k", r.get_json()["fields"])

    def test_unknown_topic(self):
        r = self.post({"query": QUERY, "topic": "Cooking"})
        self.assertEqual(r.status_code, 422)
        self.assertIn("Unknown topic", r.get_json()["fields"]["topic"])

    def test_several_errors_reported_together(self):
        r = self.post({"query": "", "top_k": 99})
        self.assertEqual(set(r.get_json()["fields"]), {"query", "top_k"})

    def test_body_not_json(self):
        r = self.client.post("/api/search", data="hello", content_type="text/plain")
        self.assertEqual(r.status_code, 400)

    def test_json_but_not_an_object(self):
        r = self.post(["overfitting"])
        self.assertEqual(r.status_code, 422)
        self.assertIn("body", r.get_json()["fields"])

    # ---- CORS ----
    def test_cors_headers_present(self):
        r = self.client.get("/api/health")
        self.assertEqual(r.headers["Access-Control-Allow-Origin"], "http://localhost:5173")
        pre = self.client.options("/api/search")
        self.assertEqual(pre.status_code, 204)
        self.assertIn("POST", pre.headers["Access-Control-Allow-Methods"])


class ChunkingTests(unittest.TestCase):
    def test_long_section_is_split_with_overlap(self):
        doc = {"doc_id": "x.md", "title": "T", "topic": "General",
               "text": "## Long\n" + " ".join(f"w{i}" for i in range(300))}
        chunks = se.chunk_document(doc, max_words=120, overlap_words=25)
        self.assertGreater(len(chunks), 1)
        first, second = chunks[0]["text"].split(), chunks[1]["text"].split()
        self.assertEqual(first[-25:], second[:25])
        self.assertTrue(all(len(c["text"].split()) <= 120 for c in chunks))

    def test_headings_start_new_chunks(self):
        doc = {"doc_id": "x.md", "title": "T", "topic": "General", "text": "## A\nalpha text\n\n### B\nbeta text"}
        chunks = se.chunk_document(doc)
        self.assertEqual([c["heading"] for c in chunks], ["A", "B"])


if __name__ == "__main__":
    unittest.main()
