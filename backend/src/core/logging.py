"""Decision logging middleware for AI agents."""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.database.models import DecisionType


class DecisionLog(BaseModel):
    """Record of a decision made by an agent."""
    id: str = Field(..., description="Unique decision ID")
    agent_name: str = Field(..., description="Name of the agent making decision")
    decision_type: DecisionType
    input_context: dict[str, Any] = Field(default_factory=dict)
    decision: dict[str, Any] = Field(default_factory=dict)
    reasoning: str = ""
    outcome: Optional[str] = None
    tokens_used: int = 0
    execution_time_ms: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionLogger:
    """Middleware for logging agent decisions."""

    def __init__(self):
        self._logs: list[DecisionLog] = []

    def log_decision(
        self,
        agent_name: str,
        decision_type: DecisionType,
        input_context: dict[str, Any],
        decision: dict[str, Any],
        reasoning: str = "",
        outcome: Optional[str] = None,
        tokens_used: int = 0,
        execution_time_ms: int = 0
    ) -> DecisionLog:
        """Log a decision made by an agent."""
        log = DecisionLog(
            id=f"dec_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{len(self._logs)}",
            agent_name=agent_name,
            decision_type=decision_type,
            input_context=input_context,
            decision=decision,
            reasoning=reasoning,
            outcome=outcome,
            tokens_used=tokens_used,
            execution_time_ms=execution_time_ms
        )
        self._logs.append(log)
        return log

    def get_logs(
        self,
        agent_name: Optional[str] = None,
        decision_type: Optional[DecisionType] = None,
        limit: int = 100
    ) -> list[DecisionLog]:
        """Get decision logs with optional filtering."""
        logs = self._logs

        if agent_name:
            logs = [l for l in logs if l.agent_name == agent_name]

        if decision_type:
            logs = [l for l in logs if l.decision_type == decision_type]

        return logs[-limit:]

    def get_stats(self) -> dict[str, Any]:
        """Get statistics about logged decisions."""
        if not self._logs:
            return {"total": 0}

        total_tokens = sum(l.tokens_used for l in self._logs)
        avg_time = sum(l.execution_time_ms for l in self._logs) / len(self._logs)

        by_type = {}
        for log in self._logs:
            key = log.decision_type.value
            by_type[key] = by_type.get(key, 0) + 1

        return {
            "total": len(self._logs),
            "total_tokens": total_tokens,
            "avg_execution_time_ms": round(avg_time, 2),
            "by_type": by_type
        }

    def clear(self) -> None:
        """Clear all logs."""
        self._logs.clear()


# Global instance
decision_logger = DecisionLogger()
