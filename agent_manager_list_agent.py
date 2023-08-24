import json
from typing import Type 
from pydantic import Base, BaseModel#, Field
from sqlalchemy import inspect
from sqlalchemy.ext.declarative import DeclarativeMeta
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
    
        def json_serial(obj):
            if isinstance(obj, (datetime, date, time)):
                return obj.isoformat()
            elif isinstance(obj, timedelta):
                return str(obj)
            elif isinstance(obj, (Base, BaseModel)) or isinstance(type(obj), DeclarativeMeta):  # Handle all SQLAlchemy objects
                return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}
            elif isinstance(obj, UUID):  # Handle UUID objects.
                return str(obj)
            elif isinstance(obj, decimal.Decimal):  # Handle Decimal objects.
                return float(obj)
            elif isinstance(obj, Enum):  # Handle Enum objects.
                return obj.name
            elif isinstance(obj, InstrumentedList):  # Handle SQLAlchemy relationship objects.
                return [serialize(elem) for elem in obj]
            elif isinstance(obj, Iterable):
                return [serialize(item) for item in obj]
            raise TypeError("Type %s not serializable" % type(obj)) 
        
        def serialize(obj):
            if type(obj) is list:
                return [serialize(i) for i in obj]
            elif isinstance(obj, (str, int, float, bool)) or obj is None:
                return obj
            elif isinstance(obj, dict):
                obj = obj.copy()
                for key in obj:
                    obj[key] = serialize(obj[key])
                return obj
            else:
                return json_serial(obj)
    
        session = self.toolkit_config.session

        toolkit = session.query(Toolkit).filter(Toolkit.id == self.toolkit_config.toolkit_id).first()
        organisation = session.query(Organisation).filter(Organisation.id == toolkit.organisation_id).first()
        project = session.query(Project).filter(Project.organisation_id == organisation.id).first()
        agents = session.query(Agent).filter(Agent.project_id == project.id).all()

        json.dumps(serialize(agents), default=json_serial)
