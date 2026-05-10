"""Strategist Agent — Remediation planning and risk assessment."""

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


class RemediationAction(BaseModel):
    """A single remediation action with risk metadata."""

    action_type: str  # restart, scale, rollback, reroute, config_change
    target_service: str
    parameters: dict[str, Any]
    confidence: float
    risk_level: float  # 0.0 (safe) to 1.0 (dangerous)
    estimated_duration_seconds: int
    rollback_plan: str


class RemediationStrategy(BaseModel):
    """Complete remediation plan produced by the Strategist Agent."""

    strategy_id: str
    actions: list[RemediationAction]
    total_confidence: float
    total_risk: float
    requires_human_approval: bool
    explanation: str  # Why this strategy was chosen


@dataclass
class StrategistAgent:
    """Plans remediation strategies based on diagnosis, balancing speed against safety.

    The Strategist receives a diagnosis from the Diagnostician and produces a ranked
    list of remediation strategies. Each strategy includes risk assessment, rollback
    plans, and confidence scores that feed into the confidence gate.
    """

    llm_client: Any
    retriever: Any
    config: dict = field(default_factory=dict)
    risk_threshold: float = 0.7  # Actions above this risk level require human approval

    SYSTEM_PROMPT = """You are the Strategist Agent in the MARS self-healing system.
Your role is to plan safe, effective remediation for diagnosed incidents.

Given a diagnosis (root cause + evidence), you must:
1. Propose remediation actions (restart, scale, rollback, reroute, config change)
2. Assess risk for each action (what could go wrong?)
3. Define a rollback plan for each action
4. Estimate time to resolution
5. Assign confidence that the strategy will resolve the issue

Safety rules:
- Never propose data deletion
- Always include rollback plans
- Scope actions to affected services only (minimize blast radius)
- Prefer reversible actions over irreversible ones
- When risk is high, recommend human approval"""

    async def plan(self, diagnosis: dict, topology: dict) -> RemediationStrategy:
        """Generate a remediation strategy for the given diagnosis.

        Args:
            diagnosis: Structured diagnosis from the Diagnostician Agent.
            topology: Service dependency graph.

        Returns:
            RemediationStrategy with ordered actions and risk assessment.
        """
        # Retrieve relevant runbooks for this type of failure
        retrieved_runbooks = await self.retriever.search(
            query=f"remediation for {diagnosis['root_cause']}",
            filters={"doc_type": "runbook"},
            top_k=3,
        )

        prompt = self._build_prompt(diagnosis, retrieved_runbooks, topology)

        response = await self.llm_client.chat(
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return self._parse_response(response, diagnosis)

    def _build_prompt(
        self, diagnosis: dict, runbooks: list[dict], topology: dict
    ) -> str:
        """Construct strategy prompt with diagnosis and runbook context."""
        runbook_text = "\n\n".join(
            f"### Runbook: {rb['title']}\n{rb['content']}" for rb in runbooks
        )

        return f"""## Diagnosis
- Root cause: {diagnosis.get('root_cause', 'unknown')}
- Confidence: {diagnosis.get('confidence', 0.0):.2f}
- Affected services: {', '.join(diagnosis.get('affected_services', []))}
- Category: {diagnosis.get('suggested_category', 'unknown')}
- Evidence: {diagnosis.get('evidence', [])}

## Relevant Runbooks
{runbook_text}

## Constraints
- Risk threshold: {self.risk_threshold} (actions above this need human approval)
- Available actions: restart, scale_up, scale_down, rollback, reroute_traffic, config_change
- Blast radius must be limited to affected services

Propose a remediation strategy. Include specific actions, risk levels, and rollback plans."""

    def _parse_response(self, response: str, diagnosis: dict) -> RemediationStrategy:
        """Parse LLM response into structured RemediationStrategy."""
        # Implementation: extract structured strategy from LLM output
        ...
