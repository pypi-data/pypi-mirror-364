from typing import Any, Self

from fastmcp.tools import FunctionTool
from pydantic.type_adapter import TypeAdapter

from pydantic_ai.agent import Agent, AgentRunResult


class AgentTool[T](FunctionTool):
    @classmethod
    def from_agent(cls, agent: Agent[Any, T], name: str, description: str) -> Self:
        async def invoke_agent(task: str) -> T:
            result: AgentRunResult[T] = await agent.run(task)
            return result.output

        return cls(
            name=name,
            fn=invoke_agent,
            description=description,
            parameters={
                "task": {
                    "type": "string",
                    "description": "The task to run the agent on",
                },
            },
            output_schema=TypeAdapter(agent.output_type).json_schema(),
        )
