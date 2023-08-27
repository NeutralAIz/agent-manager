from abc import ABC
from typing import List
import traceback
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentTool
from agent_manager_current_agent import CurrentAgentTool
from agent_manager_new_run_agent import NewRunAgentTool
from agent_manager_dynamic_agent_toolkit import DynamicAgentToolkit

class AgentManagerToolkit(BaseToolkit, ABC):
    name: str = "AgentManager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."

    def get_tools(self) -> List[BaseTool]:
        dynamicAgents = []
        try:
            # targetDynamicAgentToolkit = DynamicAgentToolkit()
            # dynamicAgents = targetDynamicAgentToolkit.create_from_agents(targetDynamicAgentToolkit)

            return [
                ListAgentTool(), CurrentAgentTool(), NewRunAgentTool(), DynamicAgentToolkit()
            ]
        except:
            traceback.print_exc()
        finally:
            return [
                ListAgentTool(), CurrentAgentTool(), NewRunAgentTool()
            ]

    def get_env_keys(self) -> List[str]:
        return []
