import json

from aworld.core.agent.swarm import GraphBuildType
from aworld.core.context.base import Context
from aworld.core.task import TaskResponse
from aworld.output.outputs import DefaultOutputs
from aworld.utils.common import sync_exec
from aworld.utils.run_util import exec_tool
from examples.multi_agents.workflow.search.run import *
from examples.common.tools import Tools

agent_config = AgentConfig(
    llm_provider="openai",
    llm_model_name="gpt-4o",
    llm_temperature=1,
    llm_api_key="dummy",
    llm_base_url="http://localhost:34567",
)


def search():
    search = Agent(
        conf=agent_config,
        name="search_agent",
        system_prompt=search_sys_prompt,
        agent_prompt=search_prompt,
        tool_names=[Tools.SEARCH_API.value]
    )

    summary = Agent(
        conf=agent_config,
        name="summary_agent",
        system_prompt=summary_sys_prompt,
        agent_prompt=summary_prompt
    )
    # default is workflow swarm
    swarm = Swarm(search, summary, max_steps=1)

    prefix = ""
    # can special search google, wiki, duck go, or baidu. such as:
    # prefix = "search wiki: "
    res = Runners.sync_run(
        input=prefix + """What is an agent.""",
        swarm=swarm
    )
    print(res.answer)

def swarm():
    agent1 = Agent(name='agent1', conf=agent_config)
    agent2 = Agent(name='agent2', conf=agent_config)
    agent3 = Agent(name='agent3', conf=agent_config)
    agent4 = Agent(name='agent4', conf=agent_config)
    agent5 = Agent(name='agent5', conf=agent_config)
    agent6 = Agent(name='agent6', conf=agent_config)
    agent7 = Agent(name='agent7', conf=agent_config)
    agent8 = Agent(name='agent8', conf=agent_config)

    swarm = Swarm(agent1, [(agent2, (agent4, [agent7, agent8])), (agent3, agent5)], agent6)
    swarm.reset("")
    print(swarm.ordered_agents)

    swarm = Swarm((agent1, agent2), (agent1, agent3), (agent1, agent4), (agent1, agent5), build_type=GraphBuildType.HANDOFF)
    swarm.reset("")
    print(swarm.build_type)


if __name__ == '__main__':
    # search()
    # swarm()
    context = Context()
    outputs = DefaultOutputs()
    res: TaskResponse = sync_exec(exec_tool, "search_api", "baidu", {"query": "test"}, context, True, outputs)
    print(json.loads(res.answer))
