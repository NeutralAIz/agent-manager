from sqlalchemy.orm import Session
from typing import Any, List, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
import traceback
from agent_manager_helpers_data import get_agents, execute_save_scheduled_agent_tool, get_toolkit_by_name, add_or_update, get_agent, get_tool_by_class_name
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.lib.logger import logger
from agent_manager_helpers_resources import ResourceManager

class DynamicAgentToolInput(BaseModel):
    target_agent_id: int = Field(
        ...,
        description="The Id of the agent to execute.\n",
    )
    wait_for_result: bool = Field(
        ...,
        description="(Recommend True) Wait for the agent to finish and return the results.",
    )


def static_init(cls):
    if getattr(cls, "static_init", None):
        cls.static_init()
    return cls

@static_init
class DynamicAgentTool(BaseTool):
    name: str = "Dynamic Agent Tool"
    description: str = ""
    args_schema: Type[DynamicAgentToolInput] = DynamicAgentToolInput
    agent_id: int = None
    wait_for_result: bool = True
    class_name: str = None
    file_name: str = None
    folder_name: str = None
    agent_execution_id: int = None

    DynamicAgentToolName: str = "Dynamic Agent Tool"
    DynamicAgentToolDescription: str = ""

    @classmethod
    def static_init(cls):
        name = "Dynamic Agent Tool"
        description = "Run other agents as tools.\nAvailable Agents: (id, name, description):\n"
        if not hasattr(cls, "DynamicAgentToolName"):
            setattr(cls, "DynamicAgentToolName", name)
            setattr(cls, "name", name)
        if not hasattr(cls, "DynamicAgentToolDescription"):
            setattr(cls, "DynamicAgentToolDescription", description)
            setattr(cls, "description", description)

    def __init__(self):
        super().__init__()
        self.set_attributes()

    def set_attributes(self):
        try:
            self.name = DynamicAgentTool.DynamicAgentToolName if DynamicAgentTool.DynamicAgentToolName is not None else "Dynamic Agent Tool"

            session = None

            if not bool(self.toolkit_config) and not bool(self.toolkit_config.session):
                session = self.toolkit_config.session
            else:
                engine = connect_db()
                Session = sessionmaker(bind=engine)
                session = Session()

            target_tool = get_tool_by_class_name(session, self.__class__.__name__)

            if bool(target_tool):
                agents = get_agents(session, target_tool.toolkit_id).agents

                DynamicAgentTool.DynamicAgentToolDescription = "Run other agents as tools.\n\r<br>Available Agents: (id, name, description):\n\r<br>"
                for agent in agents:
                    DynamicAgentTool.DynamicAgentToolDescription = DynamicAgentTool.DynamicAgentToolDescription + f"{agent.id}, {agent.name}, {agent.description}\n\r<br> | "

                self.description = DynamicAgentTool.DynamicAgentToolDescription
        except:
            logger.error(traceback.print_exc())

    def _execute(self, target_agent_id: int = -1, wait_for_result: bool = True):
        self.set_attributes()

        resource_manager_obj = ResourceManager(target_agent_id, self.toolkit_config.session)
        
        files = resource_manager_obj.get_all_resources(self.agent_execution_id)

        fileList: list[str] = list[str]

        for file in files:
            fileList.extend(file.name)

        return execute_save_scheduled_agent_tool(self.toolkit_config.session, self.agent_id, self.agent_execution_id, target_agent_id, fileList, wait_for_result)