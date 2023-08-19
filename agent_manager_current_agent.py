import json
 
from typing import Type 
from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent


class CurrentAgentInput(BaseModel):
    pass


class CurrentAgentTool(BaseTool):
    """
    Current Agent tool

    Attributes:
        name : The name.
        args_schema : The args schema.
        description : The description.
        agent_id: The agent id.
        agent_execution_id : Current Execition
    """
    name: str = "Current Agent Tool"
    args_schema: Type[CurrentAgentInput] = CurrentAgentInput
    description: str = "Prints the current agent object as JSON"
    agent_id: int = None
    agent_execution_id: int = None    

    def _execute(self):
        """
        Execute the Current Agent tool.

        Returns:
            JSON representation of the current agent

        {
            "id": 1,
            "name": "MyAgent",
            "project_id": 100,
            "description": "This is an example agent",
            "agent_workflow_id": 20,
            "is_deleted": false,
            "tools": [],
            "exit": None,
            "iteration_interval": None,
            "model": None,
            "permission_type": None,
            "LTM_DB": None,
            "memory_window": None,
            "max_iterations": None,
            "user_timezone": None
        } 
        """
        agent = Agent.get_agent_from_id(session=self.toolkit_config.session, agent_id=self.agent_id)
        return json.dumps(agent, default=lambda x: x.__dict__)

