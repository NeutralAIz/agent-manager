import json
from agent_manager_helpers import json_serial
from dataclasses import dataclass, asdict
from typing import Any, Type
from pydantic import BaseModel#, Field
from sqlalchemy import inspect
from superagi.tools.base_tool import BaseTool
from superagi.models.toolkit import Toolkit
from superagi.models.agent import Agent
from superagi.models.project import Project
from superagi.models.organisation import Organisation
import decimal
from datetime import date, datetime, time, timedelta
from collections.abc import Iterable
from sqlalchemy.orm.collections import InstrumentedList
from uuid import UUID
from enum import Enum




class ListAgentInput(BaseModel):
    pass

@dataclass
class ListAgentOutput:
    organisation: Any
    project: Any
    agents: Any

    def to_json(self):
        return json.dumps(asdict(self), default=json_serial)

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
    
        session = self.toolkit_config.session

        toolkit = session.query(Toolkit).filter(Toolkit.id == self.toolkit_config.toolkit_id).first()
        organisation = session.query(Organisation).filter(Organisation.id == toolkit.organisation_id).first()
        project = session.query(Project).filter(Project.organisation_id == organisation.id).first()
        agents = session.query(Agent).filter(Agent.project_id == project.id).all()

        results = ListAgentOutput(organisation, project, agents)

        return results.to_json()
