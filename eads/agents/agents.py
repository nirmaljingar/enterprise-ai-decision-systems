
from ..core.types import AgentMessage


class Agent:
    """Deterministic multi-agent collaboration primitive."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def act(self, messages: list[AgentMessage]) -> AgentMessage:
        return AgentMessage(
            sender=self.name,
            role=self.role,
            content="acknowledged",
        )

    @staticmethod
    def swarm(messages: list[AgentMessage], tools: list[str]) -> list[AgentMessage]:
        return messages + [
            AgentMessage(
                sender="swarm",
                role="coordinator",
                content="consensus reached",
            )
        ]
