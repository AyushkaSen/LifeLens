from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import os


class BaseLLMService(ABC):
    """Abstract interface for LLM calls (meal parsing, daily synthesis).
    
    This keeps all external LLM API logic isolated, testable, and hot-swappable.
    """

    @abstractmethod
    def parse_meal_text(self, natural_text: str) -> Dict[str, Any]:
        """Extract structured meal components from natural language."""
        pass

    @abstractmethod
    def generate_daily_analysis(self, daily_context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize daily behavioral and nutrition observations with medical disclaimer."""
        pass


class MockLLMService(BaseLLMService):
    """Deterministic mock provider for Phase 1 MVP."""

    def parse_meal_text(self, natural_text: str) -> Dict[str, Any]:
        return {
            "meal_type": "Snack",
            "meal_time": None,
            "items": [
                {"food_name": "banana", "quantity": 1.0, "unit": "item"},
            ],
            "confidence": 0.95,
            "raw_text": natural_text,
            "provider": "mock",
        }

    def generate_daily_analysis(self, daily_context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "observations": [
                "Focus peak observed ~60 mins after morning protein intake.",
                "Cognitive task variance remained within 5% of historical baseline.",
            ],
            "confidence": 0.92,
            "disclaimer": (
                "Notice: LifeLens is a behavioral and productivity self-analytics tool. "
                "These observations are automated data associations and do not constitute medical, "
                "clinical, or professional dietary advice."
            ),
            "provider": "mock",
        }


def get_llm_service() -> BaseLLMService:
    """Factory to retrieve the configured LLM service provider."""
    provider = os.getenv("LIFELENS_LLM_PROVIDER", "mock").lower()
    if provider == "mock":
        return MockLLMService()
    # Ready to register GeminiLLMService / OpenAI in Phase 2
    return MockLLMService()
