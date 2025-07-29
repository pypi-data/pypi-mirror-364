from agent_expert_panel.models.config import AgentConfig
from pathlib import Path
import os

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelInfo


current_path: str = Path(__file__)
config_path: str = os.path.join(current_path.parent.parent.parent.parent, "configs")

advocate_config = AgentConfig.from_yaml(os.path.join(config_path, "advocate.yaml"))

model_client = OpenAIChatCompletionClient(
    model=advocate_config.model_name,
    base_url=advocate_config.openai_base_url,
    api_key=advocate_config.openai_api_key,
    model_info=ModelInfo(**advocate_config.model_info.model_dump()),
)

advocate = AssistantAgent(
    name="advocate",
    model_client=model_client,
    system_message=advocate_config.system_message,
    reflect_on_tool_use=advocate_config.reflect_on_tool_use,
)

if __name__ == "__main__":
    import asyncio
    from autogen_ext.ui import RichConsole

    async def main():
        await RichConsole(advocate.run_stream(task="What is the capital of France?"))

    asyncio.run(main())
