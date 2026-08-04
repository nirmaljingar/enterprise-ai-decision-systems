
from ..core.types import AgentMessage


class Agent:
    """Multi-agent collaboration primitive.

    Stub: ``act`` acknowledges without reading the messages, and ``swarm`` fans out fixed
    replies. There is no negotiation, tool selection, or shared state.
    """

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
