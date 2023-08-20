from typing import Type 
from fastapi import Depends

from fastapi_jwt_auth import AuthJWT
from fastapi_sqlalchemy import db
from pydantic import BaseModel, Field

from superagi.tools.base_tool import BaseTool
from superagi.models.agent import Agent
from superagi.helper.auth import get_user_organisation, check_auth
import json
from superagi.models.organisation import Organisation
from superagi.models.project import Project
from superagi.models.user import User

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


        user = db.session.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=400,
                                detail="User not found")
        
        targetOrganisation = Organisation.find_or_create_organisation(db.session, user)
        targetProject = Project.find_or_create_default_project(db.session, targetOrganisation.id)

        # Get all agents for default project
        agents = db.session.query(Agent).filter(Agent.project_id == targetProject.id).all()

        agent_list = [agent.__dict__ for agent in agents] 

        return json.dumps(agent_list)