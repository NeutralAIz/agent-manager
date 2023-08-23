import json
from typing import Type 
from pydantic import BaseModel#, Field
from superagi.tools.base_tool import BaseTool
from superagi.models.toolkit import Toolkit
from superagi.models.agent import Agent
from superagi.models.project import Project
from superagi.models.organisation import Organisation


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
    description: str = "Prints all the agent objects as JSON from the default project"
    agent_id: int = None
    agent_execution_id: int = None

    def _execute(self):
        """
        Execute the List Agent tool.
        Returns:
            JSON representation of all the agents from default project
        """  


        session = self.toolkit_config.session

        toolkit = session.query(Toolkit).filter(Toolkit.id == self.toolkit_config.toolkit_id).first()
        organisation = session.query(Organisation).filter(Organisation.id == toolkit.organisation_id).first()
        project = session.query(Project).filter(Project.organisation_id == organisation.id).first()
        agents = session.query(Agent).filter(Agent.project_id == project.id).all()

        # Get all agents for default project
        agent_list = [agent.__dict__ for agent in agents] 

        return json.dumps(agent_list)