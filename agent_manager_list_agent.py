import json
from typing import Type 
from pydantic import BaseModel#, Field
from superagi.tools.base_tool import BaseTool
from superagi.models.db import connect_db
from sqlalchemy.orm import sessionmaker
from superagi.helper.auth import get_user_organisation_project
#from superagi.models.agent import Agent
#from superagi.config.config import get_config

engine = connect_db()
Session = sessionmaker(bind=engine)

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
        targetProject = get_user_organisation_project()

        # Get all agents for default project
        #agents = db.session.query(Agent).filter(Agent.project_id == targetProject.id).all()

        #agent_list = [agent.__dict__ for agent in agents] 

        return targetProject  #json.dumps(agent_list)