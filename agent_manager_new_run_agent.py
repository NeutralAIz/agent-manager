import traceback
import time
from typing import Any, Type

from pydantic import BaseModel
from superagi.tools.base_tool import BaseTool
from agent_manager_helpers_data import get_agent_execution_configuration, create_agent_execution, get_agent_execution, get_agent_execution_feed


class NewRunAgentInput(BaseModel):
    target_agent_id: int
    wait_for_result: bool

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
        wait_for_result : Wait for the agent to finish and return a result.
    """
    name: str = "New Run Agent Tool"
    args_schema: Type[NewRunAgentInput] = NewRunAgentInput
    description: str = "Creates a new run for the specified agent and starts it, and waits for a result if specified."
    agent_id: int = None
    agent_execution_id: int = None
    target_agent_id: int = None
    wait_for_result: bool = True
            
    def _execute(self, target_agent_id: int, wait_for_result: bool):
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

            execution_result = None
            agent_execution_feed = None

            if wait_for_result:
                agent_execution = None

                maxWaitTime = 60 * 5 #seconds * minutes
                currentWaitTime = 0

                while maxWaitTime > currentWaitTime and agent_execution.status == None or agent_execution.status in ['CREATED', 'RUNNING']:
                    if agent_execution.status != None:
                        time.sleep(1) 
                        currentWaitTime += 1

                    agent_execution = get_agent_execution(target_agent_id, session)

                agent_execution_feed = get_agent_execution_feed(agent_execution, session)
            

        except:
            traceback.print_exc()
        finally:
            return {
                'agent_id': target_agent_id,
                'agent_execution_id': agent_execution_created.id if agent_execution_created != None else None,
                'execution': execution_result,
                'feed': agent_execution_feed,
                'resources': {
                    'input': [],
                    'output': []
                }
            }