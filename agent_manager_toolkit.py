from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentTool
from agent_manager_current_agent import CurrentAgentTool

class AgentManagerToolkit(BaseToolkit, ABC):
    name: str = "AgentManager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."

    def get_tools(self) -> List[BaseTool]:
        return [
            ListAgentTool(), CurrentAgentTool(),
        ]

    def get_env_keys(self) -> List[str]:
        return []
