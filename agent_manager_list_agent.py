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
        description : The description.
        args_schema : The args schema.
    """
    name: str = "List Agent"
    args_schema: Type[BaseModel] = ListAgentInput
    description: str = "Prints all the agent objects as JSON from the default project"

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