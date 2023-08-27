import traceback

from typing import Type
from pydantic import BaseModel
from superagi.tools.base_tool import BaseTool
from agent_manager_helpers_data import get_agents


class ListAgentInput(BaseModel):
    pass

class ListAgentTool(BaseTool):
    """
    List Agent tool
    Attributes:
        name : The name.
        args_schema : The args schema.
        description : The description.
        agent_id : Current agent id
        agent_execution : Current agent execution
    """
    name: str = "List Agent Tool"
    args_schema: Type[ListAgentInput] = ListAgentInput
    description: str = "Prints all the agent objects as JSON from the default project.."
    agent_id: int = None
    agent_execution_id: int = None
            
    def _execute(self):   
    
        """
        Execute the List Agent tool.
        Returns:
            JSON representation of all the agents from default project
        """

        try:
            agents = get_agents(self.toolkit_config.session, self.toolkit_config)
        except:
            traceback.print_exc()

        return agents.to_json() if agents != None else None

        

    