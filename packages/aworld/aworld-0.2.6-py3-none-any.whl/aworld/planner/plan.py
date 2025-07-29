# coding: utf-8
# Copyright (c) 2025 inclusionAI.
import json
import re

from aworld.core.agent.base import AgentResult
from aworld.core.agent.output_parser import AgentOutputParser
from aworld.core.common import ActionModel
from aworld.core.context.base import Context
from aworld.logs.util import logger
from aworld.models.model_response import ModelResponse
from aworld.planner.base import BasePlanner
from aworld.planner.models import Plan
from aworld.planner.parse import parse_step_json

# Tags for response structure
PLANNING_TAG = "<PLANNING_TAG>"
PLANNING_END_TAG = "</PLANNING_TAG>"
FINAL_ANSWER_TAG = "<FINAL_ANSWER_TAG>"
FINAL_ANSWER_END_TAG = "</FINAL_ANSWER_TAG>"

# Default system prompt
DEFAULT_SYSTEM_PROMPT = f"""When answering questions, please follow these two steps:

1. First, output an execution plan in JSON format between {PLANNING_TAG} and {PLANNING_END_TAG}:
{{
  "steps": {{
    "agent_step_1": {{"input": "step description", "id": "tool_name"}},
    "agent_step_2": {{"input": "step description", "id": "tool_name"}},
    "agent_step_3": {{"input": "step description", "id": "tool_name"}}
  }},
  "dag": ["agent_step_1","agent_step_2","agent_step_3"]
}}

Where:
- steps: Contains each step's description and executor ID
  * "id" MUST be a valid tool name from the available tools list below
  * "input" describes what this step should accomplish
- dag: Defines the execution order and dependencies between steps in "steps"
  * Each element in dag refers to step keys in "steps"
  * You MUST follow the json format in the example above

2. Then, provide the final answer between {FINAL_ANSWER_TAG} and {FINAL_ANSWER_END_TAG}:
- The answer should be accurate and meet the query requirements
- If unable to answer using existing tools and information, explain why and request more information
- Prioritize using information already available in the context to avoid redundant tool calls

Available Tools:
{{{{tool_list}}}}

User Input: {{{{task}}}}"""


class DefaultPlanner(BasePlanner):
    """The LLM model for planning."""
    plan_system_prompt: str = DEFAULT_SYSTEM_PROMPT
    replan_system_prompt: str = DEFAULT_SYSTEM_PROMPT

    def __init__(self, plan_system_prompt: str = DEFAULT_SYSTEM_PROMPT, replan_system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.plan_system_prompt = plan_system_prompt
        self.replan_system_prompt = replan_system_prompt

    def plan(self, context: "Context") -> str:
        """Build the plan instruction."""
        return self.plan_system_prompt
    def replan(self, context: "Context") -> str:
        """Build the plan instruction."""
        return self.replan_system_prompt


class PlannerOutputParser(AgentOutputParser):
    """Parser for responses that include thinking process and planning."""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name

    def parse(self, resp: ModelResponse) -> AgentResult:
        if not resp or not resp.content:
            logger.warning("No valid response content!")
            return AgentResult(actions=[], current_state=None)

        content = resp.content.strip()

        # Extract planning section
        planning_match = re.search(r'<PLANNING_TAG>(.*?)</PLANNING_TAG>', content, re.DOTALL)
        final_answer_match = re.search(r'<FINAL_ANSWER_TAG>(.*?)</FINAL_ANSWER_TAG>', content, re.DOTALL)
        step_json = ""
        if planning_match:
            step_json = planning_match.group(1).strip()
        final_answer = ""
        if final_answer_match:
            final_answer = final_answer_match.group(1).strip()

        actions = []
        is_call_tool = False

        # Parse planning section if exists
        if step_json or final_answer:
            try:
                step_infos = parse_step_json(step_json)
                plan = Plan(step_infos=step_infos, answer=final_answer)
                logger.info(f"BuiltInPlannerOutputParser|plan|{plan.json()}")
                actions.append(ActionModel(
                    agent_name=self.agent_name,
                    policy_info=plan.model_dump_json()
                ))
            except json.JSONDecodeError:
                logger.warning("Failed to parse planning JSON")

        # If neither planning nor final answer found, use entire content
        if not actions:
            actions.append(ActionModel(
                agent_name=self.agent_name,
                policy_info=content
            ))

        logger.info(f"BuiltInPlannerOutputParser|actions|{actions}")

        return AgentResult(actions=actions, current_state=None, is_call_tool=is_call_tool)
