from abc import ABC
from typing import List
import traceback
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentTool
from agent_manager_current_agent import CurrentAgentTool
from agent_manager_new_run_agent import NewRunAgentTool
from agent_manager_dynamic_agent import DynamicAgentTool
from superagi.lib.logger import logger

class AgentManagerToolkit(BaseToolkit, ABC):
    name: str = "Agent Manager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."
    dynamicAgentsOnLoad: List[BaseTool] = List[BaseTool]
        
    def get_tools(self) -> List[BaseTool]:
        return [
            ListAgentTool(), CurrentAgentTool(), NewRunAgentTool(), DynamicAgentTool()
        ]

    def get_env_keys(self) -> List[str]:
        return []
