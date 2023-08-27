
from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.models.agent import Agent
from superagi.tools.base_tool import BaseTool
import traceback
from agent_manager_helpers_data import get_agents, execute_save_scheduled_agent_tool


class DynamicAgentToolkitInput(BaseModel):
    wait_for_result: bool = Field(
        ...,
        description="(Recommended) Wait for the agent to finish and return the results.",
    )


class DynamicAgentToolkit(BaseTool):
    name: str = "Dynamic Agent Toolkit"
    args_schema: Type[DynamicAgentToolkitInput] = DynamicAgentToolkitInput
    description: str = "Executes save scheduled agent tool for each agent object in the default project."
    agent_id: int = None
    wait_for_result: bool = True

    def __init__(self, agent: Agent):
        self.name = agent.name
        self.description = agent.description
        self.agent_id = agent.id

    def _execute(self):
        return execute_save_scheduled_agent_tool(self.session, self.id)

    @staticmethod
    def create_from_agents():
        dynamic_agent_toolkits = []
        self = BaseTool()
        try:
            agents = get_agents()

            for agent in agents.agents:
                DynamicAgentToolkitClass = type(f'DynamicAgentToolkit{agent.id}', (DynamicAgentToolkit,), {'agent_id': agent.id})
                dynamic_agent_toolkit = DynamicAgentToolkitClass(agent)
                dynamic_agent_toolkits.append(dynamic_agent_toolkit)

        except:
            traceback.print_exc()
        finally:
            return dynamic_agent_toolkits

        