from typing import Type 
from fastapi import Depends

from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.models.project import Project
from superagi.helper.auth import get_user_organisation, check_auth
import json

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

    def _execute(self, Authorize: AuthJWT = Depends(check_auth)):
        """
        Execute the List Agent tool.
        Returns:
            JSON representation of all the agents from default project
        """  
        # Get current user organisation
        organisation = get_user_organisation(Authorize)

        # Get default project for the organisation
        default_project = Project.find_or_create_default_project(db.session, organisation.id)

        # Get all agents for default project
        agents = db.session.query(Agent).filter(Agent.project_id == default_project.id).all()

        agent_list = [agent.__dict__ for agent in agents] 

        return json.dumps(agent_list)