"""Base agent class for AI News Influencer agents."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

from src.database.models import AgentDecision, DecisionType


InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


class AgentContext(BaseModel):
    """Context passed to agents for decision making."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    session_id: str = ""
    previous_decisions: list[AgentDecision] = Field(default_factory=list)
    system_config: dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel, Generic[OutputT]):
    """Result from an agent execution."""
    success: bool
    output: OutputT | None = None
    error: str | None = None
    reasoning: str = ""
    tokens_used: int = 0
    execution_time_ms: int = 0


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """Base class for all AI agents."""

    name: str = "BaseAgent"
    description: str = "Base agent class"
    decision_type: DecisionType = DecisionType.CONTENT_SELECTION

    def __init__(self, context: AgentContext | None = None):
        self.context = context or AgentContext()
        self._decision_log: list[AgentDecision] = []

    @abstractmethod
    async def execute(self, input_data: InputT) -> AgentResult[OutputT]:
        """Execute the agent's main task."""
        pass

    async def run(self, input_data: InputT) -> AgentResult[OutputT]:
        """Run the agent with logging and error handling."""
        start_time = datetime.utcnow()

        try:
            result = await self.execute(input_data)

            # Log the decision
            decision = AgentDecision(
                id=0,  # Will be set by database
                decision_type=self.decision_type,
                input_context=input_data.model_dump(),
                decision=result.output.model_dump() if result.output else {},
                reasoning=result.reasoning,
                outcome="success" if result.success else "failure"
            )
            self._decision_log.append(decision)

            return result

        except Exception as e:
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            return AgentResult(
                success=False,
                error=str(e),
                execution_time_ms=execution_time
            )

    @property
    def decisions(self) -> list[AgentDecision]:
        """Get all decisions made by this agent."""
        return self._decision_log
