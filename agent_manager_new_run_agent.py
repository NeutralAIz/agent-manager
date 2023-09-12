import traceback
from typing import Any, List, Type, Optional

from pydantic import BaseModel, Field
from superagi.tools.base_tool import BaseTool
from agent_manager_helpers_data import execute_save_scheduled_agent_tool



class NewRunAgentInput(BaseModel):
    target_agent_id: int = Field(
        ...,
        description="The agent id to create a run for.",
    )
    files_for_agent_run: list[str] = Field(
        ...,
        description="A list of files to attach to the execution.",
    )
    wait_for_complete: bool = Field(
        ...,
        description="(Recommended) Wait for the agent to finish",
    )
    return_feed: Optional(bool) = Field(
        ...,
        description="Return the result feed (requires wait for finish to be true).",
    )

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
        wait_for_result : Wait for the agent to finish and return a result.
    """
    name: str = "New Run Agent Tool"
    args_schema: Type[NewRunAgentInput] = NewRunAgentInput
    description: str = "Creates a new run for the specified agent and starts it, and waits for a result if specified."
    agent_id: int = None
    agent_execution_id: int = None
    target_agent_id: int = None
    wait_for_result: bool = True
            
    def _execute(self, target_agent_id: int, files_for_agent_run: list[str] = [], wait_for_complete: bool = True, return_feed: bool = True):
        """
        Execute the Save Scheduled Agent Tool.
        Returns:
            JSON representation of the agent ID
        """
        return execute_save_scheduled_agent_tool(self.toolkit_config.session, self.agent_id, self.agent_execution_id, target_agent_id, files_for_agent_run, wait_for_complete, return_feed)
    