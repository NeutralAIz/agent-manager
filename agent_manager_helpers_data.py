from typing import Any, Optional, Union, List
from datetime import datetime
from time import time
from sqlalchemy import func, or_, desc
from sqlalchemy.sql import asc
from agent_manager_helpers import json_serial
from dataclasses import dataclass, asdict
import re
import json
import traceback

from pydantic import BaseModel

from superagi.models.agent import Agent
from superagi.models.agent_config import AgentConfiguration
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_config import AgentExecutionConfiguration
from superagi.models.workflows.agent_workflow import AgentWorkflow
from superagi.models.workflows.iteration_workflow import IterationWorkflow
from superagi.worker import execute_agent
from superagi.models.agent_execution_permission import AgentExecutionPermission
from superagi.helper.feed_parser import parse_feed
from superagi.models.agent_execution import AgentExecution
from superagi.models.agent_execution_feed import AgentExecutionFeed
from superagi.models.toolkit import Toolkit
from superagi.models.agent import Agent
from superagi.models.project import Project
from superagi.models.organisation import Organisation
from agent_manager_helpers_resources import ResourceManager
from superagi.helper.time_helper import get_time_difference

@dataclass
class ListAgentOutput:
    toolkit: Any
    organisation: Any
    project: Any
    agents: Any

    def to_json(self):
        return json.dumps(asdict(self), default=json_serial)
    
def get_agents(session, toolkit_id):
    toolkit = get_toolkit(session, toolkit_id)
    organisation = get_organisation(session, toolkit.organisation_id)
    project = get_project_by_organisation_id(session, toolkit.organisation_id)
    agents = get_agents_by_project_id(session, project.id)

    return ListAgentOutput(toolkit, organisation, project, agents)


def get_toolkit(session, toolkit_id):
    return session.query(Toolkit).filter(Toolkit.id == toolkit_id).first()

def get_organisation(session, organisation_id):
    return session.query(Organisation).filter(Organisation.id == organisation_id).first()

def get_project_by_organisation_id(session, organisation_id):
    return session.query(Project).filter(Project.organisation_id == organisation_id).first()

def get_agents_by_project_id(session, project_id):
    return session.query(Agent).filter(Agent.project_id == project_id).all()

def get_toolkit_by_name(session, toolkit_name):
    toolkit = session.query(Toolkit).filter_by(name=toolkit_name).first()
    return toolkit


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

def create_agent_execution(agent_id: int, agent_config_in: AgentExecutionIn, session):
    """
    Create a new agent execution/run.

    Args:
        agent_execution (AgentExecution): The agent execution data.
    """

    # Checking if the agent exists
    agent = session.query(Agent).filter(Agent.id == agent_id, Agent.is_deleted == False).first()
    if not agent:
        print("Agent not found")
        return None

    start_step = AgentWorkflow.fetch_trigger_step_id(session, agent.agent_workflow_id)
    iteration_step_id = IterationWorkflow.fetch_trigger_step_id(session, start_step.action_reference_id).id if start_step.action_type == "ITERATION_WORKFLOW" else -1

    db_agent_execution = AgentExecution(status="RUNNING", last_execution_time=datetime.now(),
                                        agent_id=agent_id, name=agent_config_in['name'], num_of_calls=0,
                                        num_of_tokens=0,
                                        current_agent_step_id=start_step.id,
                                        iteration_workflow_step_id=iteration_step_id)

    agent_execution_configs = {
        "goal": agent_config_in['goal'],
        "instruction": agent_config_in['instruction']
    }

    agent_configs = session.query(AgentConfiguration).filter(AgentConfiguration.agent_id == agent_id).all()
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
    AgentExecutionConfiguration.add_or_update_agent_execution_config(session=session, execution=db_agent_execution, agent_execution_configs=agent_execution_configs)

    if db_agent_execution.status == "RUNNING":
        execute_agent.delay(db_agent_execution.id, datetime.now())

    return db_agent_execution

def get_agent_execution(agent_execution_id: int, session):
    """
    Get an agent execution by agent_execution_id.

    Args:
        agent_execution_id (int): The ID of the agent execution.

    Returns:
        AgentExecution: The requested agent execution.

    Raises:
        HTTPException (Status Code=404): If the agent execution is not found.
    """


    if (
        db_agent_execution := session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    ):
        return db_agent_execution
    else:
        raise Exception()
    
def get_agent_execution_feed(agent_execution_id: int, session):
    """
    Get agent execution feed with other execution details.

    Args:
        agent_execution_id (int): The ID of the agent execution.

    Returns:
        dict: The agent execution status and feeds.

    Raises:
        HTTPException (Status Code=400): If the agent run is not found.
    """

    agent_execution = session.query(AgentExecution).filter(AgentExecution.id == agent_execution_id).first()
    if agent_execution is None:
        raise Exception()
    feeds = session.query(AgentExecutionFeed).filter_by(agent_execution_id=agent_execution_id).order_by(asc(AgentExecutionFeed.created_at)).all()
    # # parse json
    final_feeds = []
    for feed in feeds:
        if feed.feed != "" and re.search(r"The current time and date is\s(\w{3}\s\w{3}\s\s?\d{1,2}\s\d{2}:\d{2}:\d{2}\s\d{4})",feed.feed) == None :
            final_feeds.append(parse_feed(feed))

    # get all permissions
    execution_permissions = session.query(AgentExecutionPermission).filter_by(agent_execution_id=agent_execution_id).order_by(asc(AgentExecutionPermission.created_at)).all()

    permissions = [
        {
                "id": permission.id,
                "created_at": permission.created_at,
                "response": permission.user_feedback,
                "status": permission.status,
                "tool_name": permission.tool_name,
                "question": permission.question,
                "user_feedback": permission.user_feedback,
                "time_difference":get_time_difference(permission.created_at,str(datetime.now()))
        } for permission in execution_permissions
    ]
    return {
        "status": agent_execution.status,
        "feeds": final_feeds,
        "permissions": permissions
    }

def execute_save_scheduled_agent_tool(session, target_agent_id: int, wait_for_result: bool = True):
    """
    Execute the Save Scheduled Agent Tool.
    Returns:
        JSON representation of the agent ID
    """
    execution_result = None
    agent_execution_feed = None
    resources = None

    try:
        # Fetching the last configuration of the target agent
        agent_config = get_agent_execution_configuration(target_agent_id, session)
        
        # Creating a new execution of the target agent 
        agent_execution_created = create_agent_execution(target_agent_id, agent_config, session)

        if wait_for_result:
            maxWaitTime = 60 * 10 #seconds * minutes
            currentWaitTime = 0

            execution_result = get_agent_execution(agent_execution_created.id, session)

            while maxWaitTime > currentWaitTime and execution_result.status in ['CREATED', 'RUNNING']:
                time.sleep(1) 
                currentWaitTime += 1
                session.refresh(execution_result)

            agent_execution_feed = get_agent_execution_feed(agent_execution_created.id, session)

            resource_manager_obj = ResourceManager(target_agent_id, session)
            resources = resource_manager_obj.get_all_resources(execution_result.id)

    except Exception as e:
        print(f"Error occurred while executing save scheduled agent tool: {e}" + traceback.print_exc()) 
    finally:
        return {
            'agent_id': target_agent_id,
            'agent_execution_id': agent_execution_created.id if agent_execution_created != None else None,
            'execution': execution_result,
            'feed': agent_execution_feed,
            'resources': resources
        }