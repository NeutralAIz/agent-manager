import traceback
import json
import ast
from typing import Any, Type, Optional, Union, List
from datetime import datetime
from sqlalchemy import func, or_, desc
from sqlalchemy.orm import Session
from agent_manager_helpers import json_serial

from dataclasses import dataclass, asdict

from pydantic import BaseModel

from superagi.lib.logger import logger
#from superagi.controllers.types.agent_schedule import AgentScheduleInput
#from superagi.controllers.tool import ToolOut
from superagi.tools.base_tool import BaseTool
#from superagi.models.toolkit import Toolkit
from superagi.models.agent import Agent
#from superagi.models.agent_schedule import AgentSchedule
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.iteration_workflow import IterationWorkflow
#from superagi.models.tool import Tool
#from superagi.models.knowledges import Knowledges
from superagi.worker import execute_agent
#from superagi.apm.event_handler import EventHandler
#from superagi.helper.auth import check_auth
#from superagi.helper.time_helper import get_time_difference

def get_agent_execution_configuration(agent_id: Union[int, None, str], session):
    """
    Get the agent configuration using the agent ID and the agent execution ID.

    Args:
        agent_id (int): Identifier of the agent.
        db: SQLAlchemy database session.

    Returns:
        dict: Agent configuration including its details.

    Raises:
        ValueError: If the agent is not found or deleted.
        ValueError: If the agent_id or the agent_execution_id is undefined.
    """
    # Checking if agent_id is defined
    if isinstance(agent_id, str):
        raise ValueError("Agent Id undefined")

    # Fetching agent data
    agent = session.query(Agent).filter(agent_id == Agent.id, or_(Agent.is_deleted == False)).first()
    if not agent:
        raise ValueError("Agent not found")

    # Setting agent_execution_id to the most recent agent execution
    agent_execution = session.query(AgentExecution).filter(AgentExecution.agent_id == agent_id).order_by(desc(AgentExecution.created_at)).first()
    if agent_execution: 
        agent_execution_id = agent_execution.id
    else:
        agent_execution_id = -1

    # Fetching agent execution id from the AgentExecution record
    if agent_execution_id != -1: 
        agent_execution_config = AgentExecution.get_agent_execution_from_id(session, agent_execution_id)
        if agent_execution_config is None:
            raise ValueError("Agent Execution not found")
        agent_id_from_execution_id = agent_execution_config.agent_id
        if agent_id != agent_id_from_execution_id:
            raise ValueError("Wrong agent id")

    # Querying the AgentConfiguration and AgentExecuitonConfiguration tables for all the keys
    results_agent = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
    if agent_execution_id!=-1: 
        results_agent_execution = session.query(AgentExecutionConfiguration).filter(AgentExecutionConfiguration.agent_execution_id == agent_execution_id).all()
    
    total_calls = session.query(func.sum(AgentExecution.num_of_calls)).filter(
        AgentExecution.agent_id == agent_id).scalar()
    total_tokens = session.query(func.sum(AgentExecution.num_of_tokens)).filter(
        AgentExecution.agent_id == agent_id).scalar()
    
    response = {}
    if agent_execution_id!=-1: 
        response = AgentExecutionConfiguration.build_agent_execution_config(session, agent, results_agent, results_agent_execution, total_calls, total_tokens)
    else: 
        response = AgentExecutionConfiguration.build_scheduled_agent_execution_config(session, agent, results_agent, total_calls, total_tokens)
        
    # Closing the session
    session.close()

    return response

class AgentExecutionIn(BaseModel):
    status: Optional[str]
    name: Optional[str]
    agent_id: Optional[int]
    last_execution_time: Optional[datetime]
    num_of_calls: Optional[int]
    num_of_tokens: Optional[int]
    current_agent_step_id: Optional[int]
    permission_id: Optional[int]
    goal: Optional[List[str]]
    instruction: Optional[List[str]]

    class config:
        orm_mode = True

def create_agent_execution(agent_execution: AgentExecutionIn, session):
    """
    Create a new agent execution/run.

    Args:
        agent_execution (AgentExecution): The agent execution data.
    """

    # Checking if the agent exists
    agent = session.query(Agent).filter(Agent.id == agent_execution.agent_id, Agent.is_deleted == False).first()
    if not agent:
        print("Agent not found")
        return None

    start_step = AgentWorkflow.fetch_trigger_step_id(db.session, agent.agent_workflow_id)
    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(
        session, start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_execution.agent_id, name=agent_execution.name, num_of_calls=0,
                                        num_of_tokens=0,
                                        current_agent_step_id=start_step.id,
                                        iteration_workflow_step_id=iteration_step_id)

    agent_execution_configs = {
        "goal": agent_execution.goal,
        "instruction": agent_execution.instruction
    }

    agent_configs = session.query(AgentConfiguration).filter(
        AgentConfiguration.agent_id == agent_execution.agent_id).all()
    keys_to_exclude = ["goal", "instruction"]
    for agent_config in agent_configs:
        if agent_config.key not in keys_to_exclude:
            if agent_config.key == "toolkits":
                if agent_config.value:
                    toolkits = [
                        int(item) for item in agent_config.value.strip('{}').split(',') if item.strip() and item != '[]']
                    agent_execution_configs[agent_config.key] = toolkits
                else:
                    agent_execution_configs[agent_config.key] = []
            elif agent_config.key == "constraints":
                if agent_config.value:
                    agent_execution_configs[agent_config.key] = agent_config.value
                else:
                    agent_execution_configs[agent_config.key] = []
            else:
                agent_execution_configs[agent_config.key] = agent_config.value

    session.add(db_agent_execution)
    session.commit()
    session.flush()
    AgentExecutionConfiguration.add_or_update_agent_execution_config(
        session=session, execution=db_agent_execution, agent_execution_configs=agent_execution_configs)

    organisation = agent.get_agent_organisation(session)

    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution
class NewRunAgentInput(BaseModel):
    target_agent_id: int

class NewRunAgentTool(BaseTool):
    """
    New Run Agent tool
    Attributes:
        name : The name.
        args_schema : The args schema.
        description : The description.
        agent_id : Current agent id
        agent_execution : Current agent execution
        target_agent_id : Target agent to create new run for
    """
    name: str = "New Run Agent Tool"
    args_schema: Type[NewRunAgentInput] = NewRunAgentInput
    description: str = "Creates a new run for the specified agent and starts it."
    agent_id: int = None
    agent_execution_id: int = None
    target_agent_id: int = None
            
    def _execute(self, target_agent_id: int):
        """
        Execute the Save Scheduled Agent Tool.
        Returns:
            JSON representation of the agent ID
        """
        try:

            session = self.toolkit_config.session

            # Fetching the last configuration of the target agent
            agent_config = get_agent_execution_configuration(target_agent_id, session)
            agent_execution_config_json = json.dumps(agent_config, default=json_serial)

            # Creating a new execution of the target agent 
            agent_execution_created = create_agent_execution(json.loads(agent_execution_config_json), session)

        except:
            traceback.print_exc()
        finally:
            return {
                'agent_id': target_agent_id,
                'agent_execution_id': agent_execution_created.id
            }