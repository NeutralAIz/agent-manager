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

    def get_tools(self) -> List[BaseTool]:
        dynamicAgents = []
        try:
            targetDynamicAgentToolkit = DynamicAgentTool()
            dynamicAgents = targetDynamicAgentToolkit.create_from_agents(self.name)

            return [
                ListAgentTool(), CurrentAgentTool(), NewRunAgentTool(), DynamicAgentTool()
            ] + dynamicAgents
        except:
            traceback.print_exc()
        finally:
            return [
                ListAgentTool(), CurrentAgentTool(), NewRunAgentTool()
            ]

    def get_env_keys(self) -> List[str]:
        return []
