"""Observer Agent — Anomaly detection and signal fusion across telemetry streams."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AnomalyAlert(BaseModel):
    """Structured alert produced by the Observer Agent."""

    alert_id: str
    timestamp: datetime
    severity: str  # critical, high, medium, low
    affected_services: list[str]
    signal_sources: list[str]  # metrics, logs, traces
    description: str
    metrics_snapshot: dict[str, float]
    correlated_events: list[dict[str, Any]]
    impact_radius: int  # estimated number of affected downstream services


@dataclass
class ObserverAgent:
    """Monitors system telemetry and detects anomalies through contextual signal fusion.

    Unlike threshold-based alerting, the Observer considers temporal context
    (time-of-day, deployment schedules), spatial context (correlated anomalies
    across services), and severity based on the service dependency graph.
    """

    llm_client: Any
    config: dict = field(default_factory=dict)
    topology: dict = field(default_factory=dict)

    SYSTEM_PROMPT = """You are the Observer Agent in the MARS self-healing system.
Your role is to analyze raw telemetry data (metrics, logs, traces) and determine
whether an anomaly exists that requires investigation.

You must output:
1. Whether this is a true anomaly or noise (considering time-of-day patterns)
2. Severity assessment (critical/high/medium/low)
3. Affected services and estimated blast radius
4. A concise description for the Diagnostician Agent

Be conservative — false positives waste system resources. Only flag genuine anomalies."""

    async def analyze(
        self,
        metrics: dict[str, float],
        logs: list[str],
        traces: list[dict],
        temporal_context: dict,
    ) -> AnomalyAlert | None:
        """Analyze telemetry streams and produce an alert if anomaly detected.

        Args:
            metrics: Current metric values keyed by service.metric_name
            logs: Recent log entries (last 5 minutes)
            traces: Distributed trace spans showing latency/errors
            temporal_context: Time-of-day, recent deployments, maintenance windows

        Returns:
            AnomalyAlert if anomaly detected, None otherwise.
        """
        prompt = self._build_prompt(metrics, logs, traces, temporal_context)

        response = await self.llm_client.chat(
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,  # Low temperature for consistent detection
        )

        return self._parse_response(response)

    def _build_prompt(
        self,
        metrics: dict[str, float],
        logs: list[str],
        traces: list[dict],
        temporal_context: dict,
    ) -> str:
        """Construct the analysis prompt with telemetry context."""
        return f"""## Current Telemetry Snapshot

### Metrics (last 5 min averages)
{self._format_metrics(metrics)}

### Recent Error Logs ({len(logs)} entries)
{chr(10).join(logs[-20:])}

### Trace Anomalies
{self._format_traces(traces)}

### Context
- Time: {temporal_context.get('current_time', 'unknown')}
- Recent deployments: {temporal_context.get('recent_deploys', 'none')}
- Maintenance windows: {temporal_context.get('maintenance', 'none')}
- Service topology: {len(self.topology)} services monitored

Analyze this telemetry. Is there a genuine anomaly requiring investigation?"""

    def _format_metrics(self, metrics: dict[str, float]) -> str:
        lines = []
        for key, value in sorted(metrics.items()):
            lines.append(f"  {key}: {value}")
        return "\n".join(lines) if lines else "  No metrics available"

    def _format_traces(self, traces: list[dict]) -> str:
        if not traces:
            return "  No trace anomalies detected"
        lines = []
        for t in traces[:10]:
            lines.append(f"  {t.get('service', '?')} → {t.get('operation', '?')}: "
                        f"{t.get('duration_ms', 0)}ms (p99: {t.get('p99_ms', 0)}ms)")
        return "\n".join(lines)

    def _parse_response(self, response: str) -> AnomalyAlert | None:
        """Parse LLM response into structured alert. Returns None if no anomaly."""
        # Implementation: parse structured JSON from LLM response
        # Returns None if LLM determines this is noise, not a real anomaly
        ...
