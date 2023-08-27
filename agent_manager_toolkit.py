from abc import ABC
from typing import List
import traceback
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentTool
from agent_manager_current_agent import CurrentAgentTool
from agent_manager_new_run_agent import NewRunAgentTool
from agent_manager_dynamic_agent import DynamicAgentTool

class AgentManagerToolkit(BaseToolkit, ABC):
    id: int = -1
    name: str = "Agent Manager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."
    dynamicAgents = []


    def __init__(self):
        super().__init__()
        try:
            self.name = "Agent Manager Toolkit"
            self.description = "Tools to view and interact with other SuperAGI agents in the same instance."
            targetDynamicAgentToolkit = DynamicAgentTool()
            self.dynamicAgents = targetDynamicAgentToolkit.create_from_agents(self.name)
        except:
            traceback.print_exc()

    def get_tools(self) -> List[BaseTool]:
        tools = [ListAgentTool(), CurrentAgentTool(), NewRunAgentTool(), DynamicAgentTool()]
        try:
            tools.extend(self.dynamicAgents)
        except:
            traceback.print_exc()
        finally:
            return tools

    def get_env_keys(self) -> List[str]:
        return []
