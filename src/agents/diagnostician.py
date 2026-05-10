"""Diagnostician Agent — RAG-enhanced root cause analysis."""

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel


class Diagnosis(BaseModel):
    """Structured diagnosis produced by the Diagnostician Agent."""

    root_cause: str
    confidence: float  # 0.0 to 1.0
    affected_services: list[str]
    evidence: list[str]
    reasoning_chain: list[str]
    retrieved_incidents: list[str]  # IDs of similar past incidents
    suggested_category: str  # cascading, resource, network, dependency


@dataclass
class DiagnosticianAgent:
    """Performs root cause analysis by combining LLM reasoning with retrieved knowledge.

    The Diagnostician receives an anomaly alert from the Observer and queries the
    RAG knowledge base for similar past incidents, relevant runbooks, and service
    documentation. It then reasons over this combined context to identify the most
    likely root cause.
    """

    llm_client: Any
    retriever: Any  # RAG retriever instance
    config: dict = field(default_factory=dict)

    SYSTEM_PROMPT = """You are the Diagnostician Agent in the MARS self-healing system.
Your role is to determine the root cause of a detected anomaly.

You will receive:
1. The anomaly alert from the Observer Agent
2. Retrieved context: similar past incidents, runbooks, and architecture docs

Your job:
- Identify the most likely root cause
- Provide a confidence score (0.0 to 1.0) based on evidence strength
- List the evidence supporting your diagnosis
- Show your reasoning step by step

Be precise. A wrong diagnosis leads to wrong remediation. When uncertain, say so."""

    async def diagnose(self, alert: dict, topology: dict) -> Diagnosis:
        """Analyze an anomaly alert and determine root cause.

        Args:
            alert: Structured alert from the Observer Agent.
            topology: Service dependency graph for context.

        Returns:
            Diagnosis with root cause, confidence, and evidence.
        """
        # Step 1: Retrieve relevant knowledge
        retrieved_docs = await self.retriever.search(
            query=alert["description"],
            filters={"services": alert["affected_services"]},
            top_k=5,
        )

        # Step 2: Build diagnosis prompt with retrieved context
        prompt = self._build_prompt(alert, retrieved_docs, topology)

        # Step 3: Get LLM diagnosis
        response = await self.llm_client.chat(
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        return self._parse_response(response, retrieved_docs)

    def _build_prompt(self, alert: dict, docs: list[dict], topology: dict) -> str:
        """Build the diagnosis prompt combining alert data with retrieved knowledge."""
        doc_context = "\n\n".join(
            f"### {doc['source']} (relevance: {doc['score']:.2f})\n{doc['content']}"
            for doc in docs
        )

        return f"""## Anomaly Alert
- Severity: {alert.get('severity', 'unknown')}
- Affected services: {', '.join(alert.get('affected_services', []))}
- Description: {alert.get('description', '')}
- Metrics: {alert.get('metrics_snapshot', {})}

## Retrieved Knowledge (from past incidents and runbooks)
{doc_context}

## Service Dependencies
{self._format_topology(alert.get('affected_services', []), topology)}

Based on the alert, retrieved knowledge, and service topology, what is the root cause?
Provide your confidence level and reasoning chain."""

    def _format_topology(self, services: list[str], topology: dict) -> str:
        """Show relevant portion of the service dependency graph."""
        lines = []
        for svc in services:
            deps = topology.get(svc, {})
            upstream = deps.get("upstream", [])
            downstream = deps.get("downstream", [])
            lines.append(f"  {svc}: upstream={upstream}, downstream={downstream}")
        return "\n".join(lines) if lines else "  No topology data available"

    def _parse_response(self, response: str, docs: list[dict]) -> Diagnosis:
        """Parse LLM response into structured Diagnosis."""
        # Implementation: extract structured diagnosis from LLM output
        # In production, this uses structured output parsing (JSON mode)
        ...
