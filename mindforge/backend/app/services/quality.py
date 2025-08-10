from pydantic import BaseModel
from typing import List

class QualityScore(BaseModel):
    length_score: float
    specificity_score: float
    originality_score: float
    actionability_score: float

class QualityAnalyzer:
    def analyze_response(self, response: str) -> QualityScore:
        return QualityScore(
            length_score=self._score_length(response),
            specificity_score=self._score_specificity(response),
            originality_score=self._score_originality(response),
            actionability_score=self._score_actionability(response),
        )

    def _score_length(self, response: str) -> float:
        return min(len(response) / 500.0, 1.0)

    def _score_specificity(self, response: str) -> float:
        keywords = ["because", "therefore", "specifically", "for example"]
        return min(sum(1 for k in keywords if k in response.lower()) / 4.0, 1.0)

    def _score_originality(self, response: str) -> float:
        return 0.5 if "I agree" in response else 0.8

    def _score_actionability(self, response: str) -> float:
        return 0.8 if any(x in response.lower() for x in ["step", "action", "plan"]) else 0.4

    def is_sycophantic(self, response: str, previous_responses: List[str]) -> bool:
        agreement_phrases = ["I agree", "Yes, exactly", "That's correct"]
        return any(phrase in response for phrase in agreement_phrases) and len(response) < 200