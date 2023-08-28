from sqlalchemy.orm import Session
from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
import traceback
from agent_manager_helpers_data import get_agents, execute_save_scheduled_agent_tool, get_toolkit_by_name, add_or_update, get_agent
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.lib.logger import logger

class DynamicAgentToolInput(BaseModel):
    target_agent_id: int = Field(
        ...,
        description="The Id of the target agent to launch",
    )
    wait_for_result: bool = Field(
        ...,
        description="(Recommended) Wait for the agent to finish and return the results.",
    )


class DynamicAgentTool(BaseTool):
    name: str = "Dynamic Agent Tool"
    args_schema: Type[DynamicAgentToolInput] = DynamicAgentToolInput
    description: str = "Run other agents as tools"
    agent_id: int = None
    wait_for_result: bool = True
    class_name: str = None
    file_name: str = None
    folder_name: str = None

    def __init__(self, target_agent_id: int):
        logger.info(f"Init {self.__class__.__name__} - {target_agent_id}")
        self.name = "Dynamic Agent Tool"
        self.description = "Run other agents as tools"

        # engine = connect_db()
        # Session = sessionmaker(bind=engine)
        # session = Session()

        # agent = get_agent(session, target_agent_id)

        # self.name = agent.name
        # self.description = agent.description
        # self.agent_id = agent.id
        # self.class_name = self.__class__.__name__
        # self.file_name = "agent_manager_toolkit.py"
        # self.folder_name = "agent-manager"

    # def create_from_agents(self, toolkit_name):
    #     dynamic_agent_toolkits = []

    #     try:
    #         engine = connect_db()
    #         Session = sessionmaker(bind=engine)
    #         session = Session()

    #         toolkit = get_toolkit_by_name(session, toolkit_name)

    #         logger.info(f"Toolkit info: {toolkit}")

    #         if toolkit is not None: 
    #             agents = get_agents(session, toolkit.id)

    #             logger.info(f"Agents found: {agents}")

    #             for agent in agents.agents:
    #                 DynamicAgentToolkitClass = type(f'DynamicAgent{agent.id}', (DynamicAgentTool,), {'agent_id': agent.id})
    #                 dynamic_agent_toolkit = DynamicAgentToolkitClass().build(session, agent, toolkit_name)
    #                 dynamic_agent_toolkits.append(dynamic_agent_toolkit)
    #         session.flush()
    #     except:
    #         logger.error(traceback.print_exc())
    #     finally:
    #         return dynamic_agent_toolkits

    def _execute(self, target_agent_id: int):
        return "Worked!"
        # return execute_save_scheduled_agent_tool(self.toolkit_config.session, self.agent_id)
        
    
    # def build(self, session, agent, toolkit_name):
    #     try:
    #         self.name = agent.name
    #         self.description = agent.description
    #         self.agent_id = agent.id
    #         self.class_name = self.__class__.__name__
    #         self.file_name = "agent_manager_toolkit.py"
    #         self.folder_name = "agent-manager"
    #         toolkit = get_toolkit_by_name(session, toolkit_name)

    #         tool = add_or_update(session, self.name, self.description, self.folder_name, self.class_name, self.file_name, toolkit.id)
    #         logger.info(f"Tool created {tool}")

    #     except:
    #         logger.error(traceback.print_exc())
    #     finally:
    #         return tool


    # def create_from_agents(self, toolkit_name):
    #     dynamic_agent_toolkits = []

    #     try:
    #         engine = connect_db()
    #         Session = sessionmaker(bind=engine)
    #         session = Session()

    #         toolkit = get_toolkit_by_name(session, toolkit_name)

    #         logger.info(f"Toolkit info: {toolkit}")

    #         if toolkit is not None: 
    #             agents = get_agents(session, toolkit.id)

    #             logger.info(f"Agents found: {agents}")

    #             for agent in agents.agents:
    #                 DynamicAgentToolkitClass = type(f'DynamicAgent{agent.id}', (DynamicAgentTool,), {'agent_id': agent.id})
    #                 dynamic_agent_toolkit = DynamicAgentToolkitClass().build(session, agent, toolkit_name)
    #                 dynamic_agent_toolkits.append(dynamic_agent_toolkit)
    #         session.flush()
    #     except:
    #         logger.error(traceback.print_exc())
    #     finally:
    #         return dynamic_agent_toolkits
        
        

        