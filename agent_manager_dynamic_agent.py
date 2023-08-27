from sqlalchemy.orm import Session
from typing import Any, Type
from pydantic import BaseModel, Field
from superagi.models.tool import Tool
from superagi.models.toolkit import Toolkit
from superagi.tools.base_tool import BaseTool
import traceback
from agent_manager_helpers_data import get_agents, execute_save_scheduled_agent_tool, get_toolkit_by_name
from sqlalchemy.orm import sessionmaker
from superagi.models.db import connect_db
from superagi.lib.logger import logger

class DynamicAgentToolInput(BaseModel):
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

    def _execute(self):
        return execute_save_scheduled_agent_tool(self.toolkit_config.session, self.agent_id)

    def build(self, session, agent, toolkit_name):
        try:
            self.name = agent.name
            self.description = agent.description
            self.agent_id = agent.id
            class_name = self.__class__.__name__
            toolkit = get_toolkit_by_name(session, toolkit_name)

            Tool.add_or_update(session, self.name, self.description, "agent-manager", class_name, "agent_manager_dynamic_agent.py", toolkit.id)

        except:
            traceback.print_exc()



    def create_from_agents(self, toolkit_name):
        dynamic_agent_toolkits = []

        try:
            engine = connect_db()
            Session = sessionmaker(bind=engine)
            session = Session()

            toolkit = get_toolkit_by_name(session, toolkit_name)

            logger.info(f"Toolkit info: {toolkit}")

            agents = get_agents(session, toolkit.id)

            logger.info(f"Agents found: {agents}")

            for agent in agents.agents:
                DynamicAgentToolkitClass = type(f'DynamicAgent{agent.id}', (DynamicAgentTool,), {'agent_id': agent.id})
                dynamic_agent_toolkit = DynamicAgentToolkitClass().build(session, agent, toolkit_name)
                dynamic_agent_toolkits.append(dynamic_agent_toolkit)

        except:
            logger.error(traceback.print_exc())
        finally:
            return dynamic_agent_toolkits
        
        

        