from abc import ABC
from typing import List
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentInput
from agent_manager_current_agent import CurrentAgentInput


class PyppeteerWebScrapperToolkit(BaseToolkit, ABC):
    name: str = "Agent Manager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."

    def get_tools(self) -> List[BaseTool]:
        return [
            ListAgentInput(), CurrentAgentInput(),
        ]

    def get_env_keys(self) -> List[str]:
        return []
