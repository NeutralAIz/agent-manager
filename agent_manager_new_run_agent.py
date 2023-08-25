import traceback
from typing import Any, Type

from pydantic import BaseModel
from superagi.tools.base_tool import BaseTool
from agent_manager_helpers_data import get_agent_execution_configuration, create_agent_execution


class NewRunAgentInput(BaseModel):
    target_agent_id: int

class NewRunAgentTool(BaseTool):
    """
    New Run Agent tool
    Attributes:
        name : The name.
        args_schema : The args schema.
        description : The description.
        agent_id : Current agent id
        agent_execution : Current agent execution
        target_agent_id : Target agent to create new run for
    """
    name: str = "New Run Agent Tool"
    args_schema: Type[NewRunAgentInput] = NewRunAgentInput
    description: str = "Creates a new run for the specified agent and starts it."
    agent_id: int = None
    agent_execution_id: int = None
    target_agent_id: int = None
            
    def _execute(self, target_agent_id: int):
        """
        Execute the Save Scheduled Agent Tool.
        Returns:
            JSON representation of the agent ID
        """
        try:

            session = self.toolkit_config.session

            # Fetching the last configuration of the target agent
            agent_config = get_agent_execution_configuration(target_agent_id, session)
            
            # Creating a new execution of the target agent 
            agent_execution_created = create_agent_execution(target_agent_id, agent_config, session)

            #return json.dumps(agent_execution_created, default = json_serial)
        except:
            traceback.print_exc()
        finally:
            return {
                'agent_id': target_agent_id,
                'agent_execution_id': agent_execution_created.id if agent_execution_created != None else None,
                'result': '',
                'resources': {
                    'input': [],
                    'output': []
                }
            }