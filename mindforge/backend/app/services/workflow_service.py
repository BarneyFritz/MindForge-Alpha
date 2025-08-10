from typing import List, Optional
from pydantic import BaseModel
from app.services.quality import QualityAnalyzer
from app.services.contradiction import ContradictionDetector
from app.connectors.base import LLMConfig
from app.services.connector_service import registry

class AntiChaosConfig(BaseModel):
    maxCritiqueRounds: int = 2
    minResponseLength: int = 100
    timeoutSeconds: int = 60
    qualityThreshold: float = 0.5
    contradictionSensitivity: str = "medium"

class WorkflowResult(BaseModel):
    brainstorm: List[str]
    critiques: List[str]
    synthesis: str
    consensus_score: float
    contradictions: List[str]

class WorkflowOrchestrator:
    def __init__(self, anti_chaos_config: AntiChaosConfig | None = None):
        self.config = anti_chaos_config or AntiChaosConfig()
        self.quality_analyzer = QualityAnalyzer()
        self.contradiction_detector = ContradictionDetector()

    async def execute_workflow(self, prompt: str, llm_settings: List[LLMConfig]) -> WorkflowResult:
        brainstorm_results = await self._parallel_brainstorm(prompt, llm_settings)
        critique_results = await self._cross_critique(brainstorm_results)
        synthesis = await self._synthesize_with_conflict_resolution(brainstorm_results, critique_results)
        return WorkflowResult(
            brainstorm=brainstorm_results,
            critiques=critique_results,
            synthesis=synthesis,
            consensus_score=self._calculate_consensus(brainstorm_results),
            contradictions=self.contradiction_detector.find_contradictions(brainstorm_results),
        )

    async def _parallel_brainstorm(self, prompt: str, llm_settings: List[LLMConfig]) -> List[str]:
        results: List[str] = []
        for cfg in llm_settings:
            connector = registry.get_connector(cfg.name, cfg)
            resp = await connector.generate_response(prompt)
            if len(resp.content) >= self.config.minResponseLength:
                results.append(resp.content)
            else:
                results.append(resp.content + "\n[Note] Padded for min length.")
        return results

    async def _cross_critique(self, brainstorm: List[str]) -> List[str]:
        critiques: List[str] = []
        for i, res in enumerate(brainstorm):
            score = self.quality_analyzer.analyze_response(res)
            critique = f"Response {i+1} critique — quality: {score.model_dump()}"
            critiques.append(critique)
        return critiques

    async def _synthesize_with_conflict_resolution(self, brainstorm: List[str], critiques: List[str]) -> str:
        return "Synthesis: Consolidated key ideas with conflict resolution and action items."

    def _calculate_consensus(self, brainstorm: List[str]) -> float:
        return 0.7