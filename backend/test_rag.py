"""
Unit tests for the RAG pipeline.

These tests are designed to run offline (no OpenAI API key required) by
mocking embeddings while still exercising chunking/indexing/search logic
against in-memory Qdrant.
"""

from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from rag import RAGPipeline


BASE_DIR = Path(__file__).resolve().parent.parent
RESUME_PATH = BASE_DIR / "data" / "resume.json"


def _zero_embedding(_: str) -> list[float]:
    # Must match the collection vector size (1536 for text-embedding-3-small).
    return [0.0] * 1536


class TestRAGPipelineOffline(unittest.TestCase):
    def test_chunk_index_search_offline(self) -> None:
        pipeline = RAGPipeline(openai_api_key="test", qdrant_url=":memory:")
        chunks = pipeline.chunk_resume_data(RESUME_PATH)
        self.assertGreater(len(chunks), 0)

        with patch.object(pipeline, "embed_text", side_effect=_zero_embedding):
            pipeline.index_chunks(chunks)
            results = pipeline.search("Tell me about Ben AI", limit=2, score_threshold=0.0)

        self.assertGreater(len(results), 0)
        self.assertIn("text", results[0])
        self.assertIn("title", results[0])
        self.assertIn("type", results[0])
        self.assertIn("score", results[0])


@unittest.skipUnless(
    os.getenv("RUN_INTEGRATION") == "1",
    "Integration test disabled. Set RUN_INTEGRATION=1 to enable.",
)
class TestRAGPipelineIntegration(unittest.TestCase):
    def test_chunk_index_search_real_openai(self) -> None:
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not openai_api_key:
            self.skipTest("OPENAI_API_KEY is not set.")

        # Keep integration test cheap: index only a small subset of chunks.
        pipeline = RAGPipeline(openai_api_key=openai_api_key, qdrant_url=":memory:")
        chunks = pipeline.chunk_resume_data(RESUME_PATH)
        self.assertGreater(len(chunks), 0)

        pipeline.index_chunks(chunks[:8])
        results = pipeline.search("Tell me about Ben AI", limit=3, score_threshold=0.0)
        self.assertGreater(len(results), 0)


if __name__ == "__main__":
    unittest.main()
