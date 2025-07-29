"""
Tests for the main ExpertPanel orchestration functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from agent_expert_panel.panel import ExpertPanel, DiscussionPattern, PanelResult
from autogen_agentchat.base import TaskResult
from autogen_agentchat.agents import AssistantAgent


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
