from pydantic_settings import YamlConfigSettingsSource, BaseSettings, SettingsConfigDict
from typing import Tuple, Type, Optional
from pathlib import Path
from .model_info import ModelInfo


class AgentConfig(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file="model_config.yaml", yaml_file_encoding="utf-8", case_sensitive=False
    )

    name: str
    model_name: str
    description: str
    system_message: str
    openai_base_url: str | None = None
    openai_api_key: str = ""
    timeout: float = 30.0
    model_info: Optional[ModelInfo] = None
    reflect_on_tool_use: bool = False

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings,
        env_settings,
        dotenv_settings,
        file_secret_settings,
    ) -> Tuple:
        """
        Define the order and sources for loading settings.
        Priority order: init > yaml > env > dotenv > file_secret
        """
        yaml_settings = YamlConfigSettingsSource(
            settings_cls,
            yaml_file=settings_cls.model_config.get("yaml_file", "model_config.yaml"),
            yaml_file_encoding=settings_cls.model_config.get(
                "yaml_file_encoding", "utf-8"
            ),
        )

        return (
            init_settings,
            yaml_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )

    @classmethod
    def from_yaml(cls, yaml_file: str | Path, **kwargs) -> "AgentConfig":
        """
        Create a AgentConfig instance from a specific YAML file.

        Args:
            yaml_file: Path to the YAML configuration file
            **kwargs: Additional keyword arguments to override

        Returns:
            AgentConfig instance loaded from the YAML file
        """
        # Create YAML source manually
        yaml_source = YamlConfigSettingsSource(
            cls, yaml_file=str(yaml_file), yaml_file_encoding="utf-8"
        )

        # Load data from YAML
        yaml_data = yaml_source()

        # Merge with any provided kwargs (kwargs take precedence)
        final_data = {**yaml_data, **kwargs}

        # Create instance with the loaded data
        return cls(**final_data)
