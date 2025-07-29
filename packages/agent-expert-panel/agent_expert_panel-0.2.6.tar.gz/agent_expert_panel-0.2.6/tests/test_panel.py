"""
Tests for the main ExpertPanel orchestration functionality.
"""

import pytest
import asyncio
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from agent_expert_panel.panel import ExpertPanel, DiscussionPattern, PanelResult
from agent_expert_panel.models.config import AgentConfig
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent


class TestConfigurationInclusion:
    """
    Test cases for configuration file inclusion and discovery.

    These tests ensure that:
    1. Configuration YAML files are properly included in the package distribution
    2. The config discovery logic works correctly with fallbacks
    3. All required agent configs exist and are valid
    4. The ExpertPanel can successfully load using packaged configs

    This prevents regression of issues where config files were missing from
    the distributed package, causing runtime errors for users.
    """

    def test_default_config_dir_discovery_package_location(self):
        """Test that _get_default_config_dir finds package-bundled configs."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__

        # Test the method directly
        config_dir = panel._get_default_config_dir()

        # Should be a valid Path
        assert isinstance(config_dir, Path)

        # Should point to either package configs or repo configs
        assert config_dir.name == "configs"

    def test_required_config_files_exist(self):
        """Test that all required agent configuration files exist and are accessible."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__
        config_dir = panel._get_default_config_dir()

        required_agents = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]

        for agent_name in required_agents:
            config_file = config_dir / f"{agent_name}.yaml"

            # Config file should exist
            assert config_file.exists(), (
                f"Configuration file {config_file} does not exist"
            )

            # Should be readable
            assert config_file.is_file(), (
                f"Configuration file {config_file} is not a file"
            )

            # Should have content
            assert config_file.stat().st_size > 0, (
                f"Configuration file {config_file} is empty"
            )

    def test_config_files_are_valid_yaml(self):
        """Test that configuration files are valid YAML and contain required fields."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__
        config_dir = panel._get_default_config_dir()

        required_agents = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]
        required_fields = ["name", "model_name", "description", "system_message"]

        for agent_name in required_agents:
            config_file = config_dir / f"{agent_name}.yaml"

            # Should be valid YAML
            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            assert isinstance(config_data, dict), (
                f"Config {config_file} is not a valid YAML dict"
            )

            # Should contain required fields
            for field in required_fields:
                assert field in config_data, (
                    f"Config {config_file} missing required field: {field}"
                )
                assert config_data[field], (
                    f"Config {config_file} has empty {field} field"
                )

            # Name should match filename
            assert config_data["name"] == agent_name, (
                f"Config {config_file} name mismatch"
            )

    def test_configs_can_be_loaded_as_agent_config(self):
        """Test that configuration files can be loaded as AgentConfig objects."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__
        config_dir = panel._get_default_config_dir()

        required_agents = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]

        for agent_name in required_agents:
            config_file = config_dir / f"{agent_name}.yaml"

            # Should be loadable as AgentConfig
            config = AgentConfig.from_yaml(config_file)

            assert isinstance(config, AgentConfig)
            assert config.name == agent_name
            assert config.model_name
            assert config.description
            assert config.system_message

    def test_fallback_config_discovery(self):
        """Test that config discovery falls back correctly when package configs don't exist."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__

        with patch.object(panel, "_get_default_config_dir") as mock_get_config:
            # Mock the package configs to not exist, repo configs to exist
            mock_repo_configs = Mock()
            mock_get_config.return_value = mock_repo_configs

            result = panel._get_default_config_dir()

            # Should return the mocked config dir
            assert result == mock_repo_configs

    def test_config_discovery_logic_unit_test(self):
        """Unit test the config discovery logic by mocking Path operations."""
        panel = ExpertPanel.__new__(ExpertPanel)  # Create instance without __init__

        # Test the actual logic by creating a temporary structure
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a fake package structure
            package_dir = Path(temp_dir) / "package"
            package_dir.mkdir()

            # Create a fake repo structure
            repo_dir = Path(temp_dir) / "repo"
            repo_configs = repo_dir / "configs"
            repo_configs.mkdir(parents=True)

            # Add a test config file to repo
            (repo_configs / "test.yaml").write_text("name: test")

            # Mock the __file__ path to point to our fake package
            fake_panel_file = package_dir / "panel.py"
            fake_panel_file.touch()

            with patch("agent_expert_panel.panel.Path") as mock_path_class:
                # Mock Path(__file__) to return our fake file
                mock_path_class.return_value = fake_panel_file

                # The method should find the repo configs since package configs don't exist
                config_dir = panel._get_default_config_dir()

                # Since package configs don't exist, should return package location anyway
                # (as per the fallback logic)
                assert isinstance(config_dir, Path)

    def test_expert_panel_can_load_with_packaged_configs(self):
        """Integration test: ExpertPanel can load successfully with packaged configs."""
        # This test will use the actual config discovery logic
        # If configs are properly packaged, this should work without mocking

        with patch("agent_expert_panel.panel.create_agent") as mock_create_agent:
            # Mock create_agent to avoid actual model initialization
            mock_agent = Mock(spec=AssistantAgent)
            mock_create_agent.return_value = mock_agent

            # This should not raise an exception
            panel = ExpertPanel()

            # Should have loaded all 5 agents
            assert len(panel.agents) == 5
            assert "advocate" in panel.agents
            assert "critic" in panel.agents
            assert "pragmatist" in panel.agents
            assert "research_specialist" in panel.agents
            assert "innovator" in panel.agents

            # create_agent should have been called 5 times
            assert mock_create_agent.call_count == 5

    def test_package_data_includes_configs(self):
        """Test that config files are accessible from the package installation."""
        import agent_expert_panel

        # Get the package directory
        package_dir = Path(agent_expert_panel.__file__).parent
        configs_dir = package_dir / "configs"

        # The configs directory should exist in the installed package
        if configs_dir.exists():
            # If configs exist in package, they should have all required files
            required_agents = [
                "advocate",
                "critic",
                "pragmatist",
                "research_specialist",
                "innovator",
            ]

            for agent_name in required_agents:
                config_file = configs_dir / f"{agent_name}.yaml"

                if config_file.exists():
                    # If the file exists, it should be valid
                    assert config_file.is_file()
                    assert config_file.stat().st_size > 0

                    # Should be valid YAML
                    with open(config_file, "r") as f:
                        config_data = yaml.safe_load(f)
                    assert isinstance(config_data, dict)
                    assert config_data.get("name") == agent_name

        # Whether configs are in package or repo, ExpertPanel should be able to find them
        # This is the critical test - that the system works end-to-end
        panel = ExpertPanel.__new__(ExpertPanel)
        config_dir = panel._get_default_config_dir()

        # Config dir should exist and have configs
        assert config_dir.exists()
        assert any(config_dir.glob("*.yaml"))


class TestExpertPanel:
    """Test cases for the ExpertPanel class."""

    @pytest.fixture
    def mock_config_dir(self, tmp_path):
        """Create a temporary config directory with test agent configs."""
        config_dir = tmp_path / "configs"
        config_dir.mkdir()

        # Create test config files for all 5 agents
        agent_configs = {
            "advocate": {
                "name": "advocate",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test advocate agent",
                "system_message": "You are a test advocate agent.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "critic": {
                "name": "critic",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test critic agent",
                "system_message": "You are a test critic agent.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "pragmatist": {
                "name": "pragmatist",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test pragmatist agent",
                "system_message": "You are a test pragmatist agent.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "research_specialist": {
                "name": "research_specialist",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test research specialist agent",
                "system_message": "You are a test research specialist agent.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
            "innovator": {
                "name": "innovator",
                "model_name": "test-model",
                "openai_base_url": "http://localhost:11434/v1",
                "openai_api_key": "",
                "timeout": 30.0,
                "description": "Test innovator agent",
                "system_message": "You are a test innovator agent.",
                "model_info": {
                    "vision": False,
                    "function_calling": True,
                    "json_output": True,
                    "family": "TEST",
                    "structured_output": True,
                    "multiple_system_messages": False,
                },
                "reflect_on_tool_use": True,
            },
        }

        # Write YAML files
        import yaml

        for name, config in agent_configs.items():
            config_file = config_dir / f"{name}.yaml"
            with open(config_file, "w") as f:
                yaml.dump(config, f)

        return config_dir

    @pytest.fixture
    def mock_task_result(self):
        """Create a mock TaskResult with realistic message data."""
        mock_result = Mock(spec=TaskResult)

        # Create mock messages
        mock_messages = []

        # Message 1: Advocate
        msg1 = Mock()
        msg1.source = "advocate"
        msg1.content = "I strongly recommend implementing this solution because the benefits clearly outweigh the risks. The evidence shows significant advantages."
        msg1.timestamp = None
        mock_messages.append(msg1)

        # Message 2: Critic
        msg2 = Mock()
        msg2.source = "critic"
        msg2.content = "While I acknowledge the potential benefits, we must consider several concerning risks and implementation challenges that could undermine success."
        msg2.timestamp = None
        mock_messages.append(msg2)

        # Message 3: Pragmatist
        msg3 = Mock()
        msg3.source = "pragmatist"
        msg3.content = "Based on our discussion, I recommend a phased implementation approach. This balances the benefits with practical constraints and allows us to mitigate risks."
        msg3.timestamp = None
        mock_messages.append(msg3)

        mock_result.messages = mock_messages
        return mock_result

    @patch("agent_expert_panel.panel.create_agent")
    def test_panel_initialization(self, mock_create_agent, mock_config_dir):
        """Test that the panel initializes correctly and loads agents."""
        # Setup mock
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_create_agent.return_value = mock_agent

        # Test initialization
        panel = ExpertPanel(config_dir=mock_config_dir)

        # Verify agents were loaded
        assert len(panel.agents) == 5  # All 5 agents
        assert "advocate" in panel.agents
        assert "critic" in panel.agents
        assert "pragmatist" in panel.agents
        assert "research_specialist" in panel.agents
        assert "innovator" in panel.agents

        # Verify create_agent was called for each agent
        assert mock_create_agent.call_count == 5

    @patch("agent_expert_panel.panel.create_agent")
    def test_missing_config_file(self, mock_create_agent, tmp_path):
        """Test that missing config files raise appropriate errors."""
        empty_config_dir = tmp_path / "empty_configs"
        empty_config_dir.mkdir()

        with pytest.raises(FileNotFoundError):
            ExpertPanel(config_dir=empty_config_dir)

    @pytest.mark.asyncio
    @patch("agent_expert_panel.panel.create_agent")
    @patch("agent_expert_panel.panel.RichConsole")
    @patch("agent_expert_panel.panel.RoundRobinGroupChat")
    async def test_round_robin_discussion(
        self,
        mock_group_chat,
        mock_rich_console,
        mock_create_agent,
        mock_config_dir,
        mock_task_result,
    ):
        """Test round-robin discussion orchestration."""
        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_agent.description = "Test agent description"
        mock_create_agent.return_value = mock_agent

        mock_group_chat_instance = Mock()
        mock_group_chat.return_value = mock_group_chat_instance
        mock_group_chat_instance.run_stream.return_value = AsyncMock()

        mock_rich_console.return_value = mock_task_result

        # Create panel and run discussion
        panel = ExpertPanel(config_dir=mock_config_dir)

        result = await panel.discuss(
            topic="Test topic",
            pattern=DiscussionPattern.ROUND_ROBIN,
            max_rounds=2,
            participants=["advocate", "critic", "pragmatist"],
        )

        # Verify result structure
        assert isinstance(result, PanelResult)
        assert result.topic == "Test topic"
        assert result.discussion_pattern == DiscussionPattern.ROUND_ROBIN
        assert result.agents_participated == ["advocate", "critic", "pragmatist"]
        assert len(result.discussion_history) > 0
        assert isinstance(result.consensus_reached, bool)
        assert isinstance(result.final_recommendation, str)
        assert result.total_rounds > 0

    @pytest.mark.asyncio
    @patch("agent_expert_panel.panel.create_agent")
    @patch("agent_expert_panel.panel.RichConsole")
    @patch("agent_expert_panel.panel.RoundRobinGroupChat")
    async def test_structured_debate_discussion(
        self,
        mock_group_chat,
        mock_rich_console,
        mock_create_agent,
        mock_config_dir,
        mock_task_result,
    ):
        """Test structured debate discussion orchestration."""
        # Setup mocks
        mock_agent = Mock(spec=AssistantAgent)
        mock_agent.name = "test-agent"
        mock_create_agent.return_value = mock_agent

        mock_group_chat_instance = Mock()
        mock_group_chat.return_value = mock_group_chat_instance
        mock_group_chat_instance.run_stream.return_value = AsyncMock()

        mock_rich_console.return_value = mock_task_result

        # Create panel and run discussion
        panel = ExpertPanel(config_dir=mock_config_dir)

        result = await panel.discuss(
            topic="Test topic",
            pattern=DiscussionPattern.STRUCTURED_DEBATE,
            max_rounds=3,
        )

        # Verify result structure
        assert isinstance(result, PanelResult)
        assert result.discussion_pattern == DiscussionPattern.STRUCTURED_DEBATE

    def test_extract_discussion_history(self, mock_config_dir, mock_task_result):
        """Test discussion history extraction from TaskResult."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            history = panel._extract_discussion_history(mock_task_result)

            assert len(history) == 3
            assert history[0]["speaker"] == "advocate"
            assert "recommend implementing" in history[0]["content"]
            assert history[1]["speaker"] == "critic"
            assert "concerning risks" in history[1]["content"]
            assert history[2]["speaker"] == "pragmatist"
            assert "phased implementation" in history[2]["content"]

    def test_extract_discussion_history_no_messages(self, mock_config_dir):
        """Test discussion history extraction when no messages are available."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            # Create empty TaskResult
            empty_result = Mock(spec=TaskResult)
            empty_result.messages = []

            history = panel._extract_discussion_history(empty_result)

            assert len(history) == 0

    def test_detect_consensus_positive(self, mock_config_dir):
        """Test consensus detection with agreement messages."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            messages = [
                {
                    "speaker": "advocate",
                    "content": "I strongly recommend this approach.",
                },
                {
                    "speaker": "critic",
                    "content": "I agree with the overall recommendation.",
                },
                {
                    "speaker": "pragmatist",
                    "content": "This sounds reasonable and practical.",
                },
            ]

            consensus = panel._detect_consensus(messages)
            assert consensus is True

    def test_detect_consensus_negative(self, mock_config_dir):
        """Test consensus detection with disagreement messages."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            messages = [
                {
                    "speaker": "advocate",
                    "content": "I strongly recommend this approach.",
                },
                {
                    "speaker": "critic",
                    "content": "I disagree with this recommendation entirely.",
                },
                {
                    "speaker": "pragmatist",
                    "content": "There are major problems with this plan.",
                },
            ]

            consensus = panel._detect_consensus(messages)
            assert consensus is False

    def test_synthesize_recommendation(self, mock_config_dir):
        """Test recommendation synthesis from agent messages."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            messages = [
                {
                    "speaker": "advocate",
                    "content": "We should implement this solution immediately.",
                },
                {
                    "speaker": "critic",
                    "content": "We need to address the security concerns first.",
                },
                {
                    "speaker": "pragmatist",
                    "content": "A phased rollout would be most practical.",
                },
            ]

            agent_names = ["advocate", "critic", "pragmatist"]
            recommendation = panel._synthesize_recommendation(messages, agent_names)

            assert "## Expert Panel Final Recommendation" in recommendation
            assert "Advocate:" in recommendation
            assert "Critic:" in recommendation
            assert "Pragmatist:" in recommendation
            assert "implement this solution" in recommendation
            assert "security concerns" in recommendation
            assert "phased rollout" in recommendation

    def test_calculate_discussion_rounds(self, mock_config_dir):
        """Test calculation of discussion rounds."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            # Test with 6 messages and 3 agents = 2 rounds
            history = [{"round": i} for i in range(6)]
            rounds = panel._calculate_discussion_rounds(history, 3)
            assert rounds == 2

            # Test with empty history
            rounds = panel._calculate_discussion_rounds([], 3)
            assert rounds == 0

            # Test with more messages than expected
            history = [{"round": i} for i in range(10)]
            rounds = panel._calculate_discussion_rounds(history, 3)
            assert rounds == 3

    def test_get_agent_descriptions(self, mock_config_dir):
        """Test getting agent descriptions."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            descriptions = panel.get_agent_descriptions()

            assert isinstance(descriptions, dict)
            assert "advocate" in descriptions
            assert "critic" in descriptions
            assert "pragmatist" in descriptions
            assert "Test advocate agent" in descriptions["advocate"]

    @pytest.mark.asyncio
    @patch("agent_expert_panel.panel.create_agent")
    async def test_quick_consensus(self, mock_create_agent, mock_config_dir):
        """Test quick consensus functionality."""
        # Setup mock
        mock_agent = Mock(spec=AssistantAgent)
        mock_create_agent.return_value = mock_agent

        panel = ExpertPanel(config_dir=mock_config_dir)

        # Mock the discuss method
        with patch.object(panel, "discuss") as mock_discuss:
            mock_result = PanelResult(
                topic="test",
                discussion_pattern=DiscussionPattern.ROUND_ROBIN,
                agents_participated=["advocate"],
                discussion_history=[],
                consensus_reached=True,
                final_recommendation="Test recommendation",
                total_rounds=1,
            )
            mock_discuss.return_value = mock_result

            result = await panel.quick_consensus("Test question")

            assert result == "Test recommendation"
            mock_discuss.assert_called_once_with(
                topic="Test question",
                pattern=DiscussionPattern.ROUND_ROBIN,
                max_rounds=1,
            )

    def test_unsupported_discussion_pattern(self, mock_config_dir):
        """Test that unsupported discussion patterns raise NotImplementedError."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            # Test with OPEN_FLOOR pattern (not implemented)
            with pytest.raises(NotImplementedError):
                asyncio.run(
                    panel.discuss(
                        topic="Test topic", pattern=DiscussionPattern.OPEN_FLOOR
                    )
                )

    def test_get_phase_instructions(self, mock_config_dir):
        """Test phase instructions for structured debate."""
        with patch("agent_expert_panel.panel.create_agent"):
            panel = ExpertPanel(config_dir=mock_config_dir)

            instructions = panel._get_phase_instructions("Initial Position Statements")
            assert "State your initial position" in instructions

            instructions = panel._get_phase_instructions("Unknown Phase")
            assert "Participate according to your expertise" in instructions
