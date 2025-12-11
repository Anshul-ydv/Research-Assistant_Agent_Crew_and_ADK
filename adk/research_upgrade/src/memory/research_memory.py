"""Simple in-memory ResearchMemory used by agents to share context and results.

This lightweight implementation provides the minimal API the workflow and
agents expect: store/get context values, store/get agent results, and retrieve
all stored results for output generation.
"""
from typing import Any, Dict, Optional


class ResearchMemory:
    def __init__(self):
        # Shared key-value contexts (e.g., research_topic, search_strategy)
        self._context: Dict[str, Any] = {}
        # Per-agent result storage
        self._agent_results: Dict[str, Any] = {}

    # Context helpers
    def store_context(self, key: str, value: Any) -> None:
        self._context[key] = value

    def get_context(self, key: str, default: Optional[Any] = None) -> Any:
        return self._context.get(key, default)

    # Agent result helpers
    def store_agent_result(self, agent_name: str, result: Any) -> None:
        self._agent_results[agent_name] = result

    def get_agent_result(self, agent_name: str) -> Optional[Any]:
        return self._agent_results.get(agent_name)

    def get_all_results(self) -> Dict[str, Any]:
        # Return a shallow copy to prevent accidental external mutation
        return dict(self._agent_results)
