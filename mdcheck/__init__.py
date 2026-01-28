"""mdcheck - Markdown checker with optional local LLM advice via Ollama"""

from mdcheck.rules import lint_with_rules
from mdcheck.ollama_client import lint_with_llm, pull_model

__version__ = "0.1.0"
__all__ = ["lint_with_rules", "lint_with_llm", "pull_model"]
