"""Executor Agent — Safe action execution with rollback guarantees."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ExecutionResult(BaseModel):
    """Outcome of a remediation execution."""

    success: bool
    action_taken: str
    target_service: str
    started_at: datetime
    completed_at: datetime
    duration_seconds: float
    rollback_triggered: bool
    health_check_passed: bool
    details: str


@dataclass
class ExecutorAgent:
    """Executes remediation actions against infrastructure with safety constraints.

    The Executor translates high-level strategy actions into concrete API calls
    (Kubernetes, cloud providers, service mesh) while enforcing:
    - Blast radius limits (only touch affected services)
    - Pre-execution rollback preparation
    - Continuous health monitoring during execution
    - Automatic rollback if health degrades
    """

    llm_client: Any
    k8s_client: Any  # Kubernetes API client
    config: dict = field(default_factory=dict)
    dry_run: bool = False  # Safety flag for testing

    SAFETY_RULES = [
        "Never delete persistent data or volumes",
        "Never scale below minimum replica count",
        "Always verify health checks after each action",
        "Halt immediately if error rate increases during remediation",
        "Maximum execution time: 5 minutes per action",
    ]

    async def execute(self, strategy: dict) -> list[ExecutionResult]:
        """Execute a remediation strategy action by action.

        Each action is executed sequentially. After each action, a health check
        runs. If health degrades, remaining actions are skipped and rollback
        begins automatically.

        Args:
            strategy: RemediationStrategy from the Strategist Agent.

        Returns:
            List of ExecutionResults, one per attempted action.
        """
        results = []

        for action in strategy.get("actions", []):
            # Prepare rollback before executing
            rollback_state = await self._capture_state(action["target_service"])

            # Execute the action
            result = await self._execute_action(action)
            results.append(result)

            # Health check after action
            healthy = await self._verify_health(action["target_service"])

            if not healthy:
                # Automatic rollback
                await self._rollback(action["target_service"], rollback_state)
                result.rollback_triggered = True
                break  # Stop executing remaining actions

        return results

    async def _execute_action(self, action: dict) -> ExecutionResult:
        """Execute a single remediation action."""
        started = datetime.utcnow()
        action_type = action.get("action_type", "unknown")
        target = action.get("target_service", "unknown")

        if self.dry_run:
            # Simulate execution without making real changes
            return ExecutionResult(
                success=True,
                action_taken=f"[DRY RUN] {action_type}",
                target_service=target,
                started_at=started,
                completed_at=datetime.utcnow(),
                duration_seconds=0.1,
                rollback_triggered=False,
                health_check_passed=True,
                details="Dry run - no changes made",
            )

        # Route to appropriate handler based on action type
        handlers = {
            "restart": self._handle_restart,
            "scale_up": self._handle_scale,
            "rollback": self._handle_rollback_deploy,
            "reroute_traffic": self._handle_reroute,
            "config_change": self._handle_config_change,
        }

        handler = handlers.get(action_type, self._handle_unknown)
        return await handler(action, started)

    async def _handle_restart(self, action: dict, started: datetime) -> ExecutionResult:
        """Restart pods for a target service via Kubernetes API."""
        target = action["target_service"]
        # Implementation: kubectl rollout restart deployment/{target}
        ...

    async def _handle_scale(self, action: dict, started: datetime) -> ExecutionResult:
        """Scale a service up or down."""
        # Implementation: adjust replica count via Kubernetes API
        ...

    async def _handle_rollback_deploy(self, action: dict, started: datetime) -> ExecutionResult:
        """Roll back to the previous deployment revision."""
        # Implementation: kubectl rollout undo deployment/{target}
        ...

    async def _handle_reroute(self, action: dict, started: datetime) -> ExecutionResult:
        """Reroute traffic away from unhealthy instances via service mesh."""
        # Implementation: update Istio VirtualService or traffic policy
        ...

    async def _handle_config_change(self, action: dict, started: datetime) -> ExecutionResult:
        """Apply a configuration change (e.g., increase connection pool, adjust timeout)."""
        # Implementation: update ConfigMap or environment variables
        ...

    async def _handle_unknown(self, action: dict, started: datetime) -> ExecutionResult:
        """Handle unrecognized action types by refusing to execute."""
        return ExecutionResult(
            success=False,
            action_taken=f"REJECTED: unknown action type '{action.get('action_type')}'",
            target_service=action.get("target_service", "unknown"),
            started_at=started,
            completed_at=datetime.utcnow(),
            duration_seconds=0.0,
            rollback_triggered=False,
            health_check_passed=False,
            details="Action type not recognized. No changes made.",
        )

    async def _capture_state(self, service: str) -> dict:
        """Capture current state for rollback purposes before making changes."""
        # Implementation: snapshot current replica count, config, traffic rules
        return {"service": service, "captured_at": datetime.utcnow().isoformat()}

    async def _verify_health(self, service: str) -> bool:
        """Run health checks after an action to confirm the service is stable."""
        # Implementation: check readiness probes, error rates, latency
        return True

    async def _rollback(self, service: str, saved_state: dict) -> None:
        """Restore a service to its pre-action state."""
        # Implementation: revert replica count, config, or deployment
        ...
