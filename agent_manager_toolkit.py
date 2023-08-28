from abc import ABC
from typing import List
import traceback
from superagi.tools.base_tool import BaseTool, BaseToolkit
from agent_manager_list_agent import ListAgentTool
from agent_manager_current_agent import CurrentAgentTool
from agent_manager_new_run_agent import NewRunAgentTool
from agent_manager_dynamic_agent import DynamicAgentTool
from superagi.lib.logger import logger

import sys
import types

class AgentManagerToolkit(BaseToolkit, ABC):
    name: str = "Agent Manager Toolkit"
    description: str = "Tools to view and interact with other SuperAGI agents in the same instance."
    dynamicAgentsOnLoad: List[BaseTool] = List[BaseTool]

    def __init__(self, class_name):
        super().__init__()        
        try:            
            self.name = "Agent Manager Toolkit"
            logger.info(f"pluginName : {self.name}")

            targetDynamicAgentToolkit = DynamicAgentTool()
            self.dynamicAgentsOnLoad = targetDynamicAgentToolkit.create_from_agents(self.name)
            
            logger.info(f"Initilizing dynamic agent tools. : {self.dynamicAgentsOnLoad}!")
            
            for dynamicAgent in self.dynamicAgentsOnLoad:
                if class_name == dynamicAgent.class_name:
                    logger.error(f"Executing : {class_name}")
                    dynamicAgent._execute()
                    return
                globals()[dynamicAgent.class_name] = dynamicAgent
                locals()[dynamicAgent.class_name] = dynamicAgent
                logger.info(f"Setting up local/global tool : {dynamicAgent}!")

        except:
            traceback.print_exc()
        
    def get_tools(self) -> List[BaseTool]:
        tools = [
            ListAgentTool(), CurrentAgentTool(), NewRunAgentTool(), DynamicAgentTool()
        ]
        try:
            tools.extend(self.dynamicAgentsOnLoad)
        except:
            traceback.print_exc()
        finally:
            return tools

    def get_env_keys(self) -> List[str]:
        return []
