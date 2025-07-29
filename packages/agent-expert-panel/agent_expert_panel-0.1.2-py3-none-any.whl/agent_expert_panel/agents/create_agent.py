"""
Used to create an agent from a config file.
"""

from agent_expert_panel.models.config import AgentConfig
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo
from autogen_agentchat.agents import AssistantAgent


def create_agent(config: AgentConfig) -> AssistantAgent:
    model_client = OpenAIChatCompletionClient(
        model=config.model_name,
        base_url=config.openai_base_url,
        api_key=config.openai_api_key,
        model_info=ModelInfo(**config.model_info.model_dump()),
    )

    agent = AssistantAgent(
        name=config.name,
        model_client=model_client,
        system_message=config.system_message,
        reflect_on_tool_use=config.reflect_on_tool_use,
    )

    return agent
