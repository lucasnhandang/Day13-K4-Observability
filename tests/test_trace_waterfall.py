from __future__ import annotations

from app.mock_llm import FakeLLM
from app.mock_rag import retrieve


def test_rag_and_llm_are_instrumented_as_nested_observations() -> None:
    assert hasattr(retrieve, "__wrapped__")
    assert hasattr(FakeLLM.generate, "__wrapped__")
