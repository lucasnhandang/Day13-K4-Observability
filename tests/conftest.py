"""Shared pytest configuration.

Tests must not export telemetry to an external Langfuse project. Unit tests that
exercise the tracing adapter use mocks and continue to verify the SDK contract.
"""

from __future__ import annotations

import os


os.environ["LANGFUSE_TRACING_ENABLED"] = "False"
