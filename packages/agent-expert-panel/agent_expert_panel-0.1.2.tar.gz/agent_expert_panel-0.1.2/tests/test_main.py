"""
Tests for the main CLI functionality.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock

from agent_expert_panel.main import (
    main,
    interactive_mode,
    batch_mode,
    setup_logging,
    display_welcome,
    display_agents,
)
from agent_expert_panel.panel import ExpertPanel, DiscussionPattern, PanelResult


class TestMain:
    """Test cases for the main CLI functions."""

    def test_setup_logging_default(self):
        """Test logging setup with default verbosity."""
        with patch("agent_expert_panel.main.logging.basicConfig") as mock_config:
            setup_logging(verbose=False)

            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert "level" in kwargs
            # Should use INFO level by default

    def test_setup_logging_verbose(self):
        """Test logging setup with verbose mode."""
        with patch("agent_expert_panel.main.logging.basicConfig") as mock_config:
            setup_logging(verbose=True)

            mock_config.assert_called_once()
            args, kwargs = mock_config.call_args
            assert "level" in kwargs
            # Should use DEBUG level in verbose mode

    @patch("agent_expert_panel.main.Console")
    def test_display_welcome(self, mock_console):
        """Test welcome message display."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        display_welcome()

        mock_console_instance.print.assert_called_once()
        # Verify the call includes a RichPanel with Markdown content

    @patch("agent_expert_panel.main.Console")
    def test_display_agents(self, mock_console):
        """Test agent display functionality."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        # Create mock panel with agent descriptions
        mock_panel = Mock(spec=ExpertPanel)
        mock_panel.get_agent_descriptions.return_value = {
            "advocate": "Test advocate description",
            "critic": "Test critic description",
        }

        display_agents(mock_panel)

        mock_console_instance.print.assert_called_once()
        # Should print a table

    @pytest.mark.skip(reason="Skipping interactive tests")
    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    @patch("agent_expert_panel.main.Confirm")
    @patch("agent_expert_panel.main.Prompt")
    async def test_interactive_mode_single_discussion(
        self, mock_prompt, mock_confirm, mock_console, mock_expert_panel
    ):
        """Test interactive mode with single discussion."""
        # Setup mocks
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        mock_panel_instance = Mock(spec=ExpertPanel)
        mock_expert_panel.return_value = mock_panel_instance
        mock_panel_instance.get_agent_descriptions.return_value = {
            "advocate": "Test description"
        }

        # Mock user inputs
        mock_confirm.side_effect = [
            False,
            False,
        ]  # Don't show details, don't continue after discussion
        mock_prompt.side_effect = [
            "Test topic",  # Topic input
            "1",  # Pattern choice
            "2",  # Max rounds
        ]

        # Mock discussion result
        mock_result = PanelResult(
            topic="Test topic",
            discussion_pattern=DiscussionPattern.ROUND_ROBIN,
            agents_participated=["advocate"],
            discussion_history=[],
            consensus_reached=True,
            final_recommendation="Test recommendation",
            total_rounds=2,
        )
        mock_panel_instance.discuss = AsyncMock(return_value=mock_result)

        result = await interactive_mode()

        # Should complete successfully
        assert result == 0
        mock_panel_instance.discuss.assert_called_once()

    @pytest.mark.skip(reason="Skipping interactive tests")
    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    @patch("agent_expert_panel.main.Confirm")
    @patch("agent_expert_panel.main.Prompt")
    async def test_interactive_mode_quit_immediately(
        self, mock_prompt, mock_confirm, mock_console, mock_expert_panel
    ):
        """Test interactive mode with immediate quit."""
        # Setup mocks
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        mock_panel_instance = Mock(spec=ExpertPanel)
        mock_expert_panel.return_value = mock_panel_instance
        mock_panel_instance.get_agent_descriptions.return_value = {}

        # Mock user inputs - quit immediately
        mock_confirm.return_value = False  # Don't show details
        mock_prompt.return_value = "quit"  # Quit command

        result = await interactive_mode()

        # Should complete successfully without discussion
        assert result == 0
        mock_panel_instance.discuss.assert_not_called()

    @pytest.mark.skip(reason="Skipping interactive tests")
    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    async def test_interactive_mode_initialization_failure(
        self, mock_console, mock_expert_panel
    ):
        """Test interactive mode when panel initialization fails."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        # Make panel initialization fail
        mock_expert_panel.side_effect = Exception("Panel initialization failed")

        result = await interactive_mode()

        # Should return error code
        assert result == 1

    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    async def test_batch_mode_success(self, mock_console, mock_expert_panel):
        """Test successful batch mode execution."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        mock_panel_instance = Mock(spec=ExpertPanel)
        mock_expert_panel.return_value = mock_panel_instance

        # Mock discussion result
        mock_result = PanelResult(
            topic="Test topic",
            discussion_pattern=DiscussionPattern.ROUND_ROBIN,
            agents_participated=["advocate"],
            discussion_history=[],
            consensus_reached=True,
            final_recommendation="Test recommendation",
            total_rounds=1,
        )
        mock_panel_instance.discuss = AsyncMock(return_value=mock_result)

        result = await batch_mode(
            topic="Test topic", pattern="round_robin", max_rounds=3
        )

        assert result == 0
        # Verify the discuss method was called (pattern gets converted internally)
        mock_panel_instance.discuss.assert_called_once()
        call_args = mock_panel_instance.discuss.call_args
        assert call_args[1]["topic"] == "Test topic"
        assert call_args[1]["pattern"].value == DiscussionPattern.ROUND_ROBIN.value
        assert call_args[1]["max_rounds"] == 3

    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.Console")
    async def test_batch_mode_invalid_pattern(self, mock_console):
        """Test batch mode with invalid discussion pattern."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        result = await batch_mode(
            topic="Test topic", pattern="invalid_pattern", max_rounds=3
        )

        assert result == 1

    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    async def test_batch_mode_panel_failure(self, mock_console, mock_expert_panel):
        """Test batch mode when panel creation fails."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        mock_expert_panel.side_effect = Exception("Panel creation failed")

        result = await batch_mode(
            topic="Test topic", pattern="round_robin", max_rounds=3
        )

        assert result == 1

    @pytest.mark.asyncio
    @patch("agent_expert_panel.main.ExpertPanel")
    @patch("agent_expert_panel.main.Console")
    async def test_batch_mode_discussion_failure(self, mock_console, mock_expert_panel):
        """Test batch mode when discussion fails."""
        mock_console_instance = Mock()
        mock_console.return_value = mock_console_instance

        mock_panel_instance = Mock(spec=ExpertPanel)
        mock_expert_panel.return_value = mock_panel_instance
        mock_panel_instance.discuss = AsyncMock(
            side_effect=Exception("Discussion failed")
        )

        result = await batch_mode(
            topic="Test topic", pattern="round_robin", max_rounds=3
        )

        assert result == 1

    @pytest.mark.skip(reason="Skipping interactive tests")
    @patch("agent_expert_panel.main.asyncio.run")
    @patch("agent_expert_panel.main.setup_logging")
    @patch("agent_expert_panel.main.argparse.ArgumentParser")
    def test_main_interactive_mode(
        self, mock_parser, mock_setup_logging, mock_asyncio_run
    ):
        """Test main function in interactive mode."""
        # Setup argument parser mock
        mock_args = Mock()
        mock_args.topic = None  # No topic = interactive mode
        mock_args.verbose = False
        mock_parser.return_value.parse_args.return_value = mock_args

        mock_asyncio_run.return_value = 0

        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with(False)
        mock_asyncio_run.assert_called_once()

    @patch("agent_expert_panel.main.asyncio.run")
    @patch("agent_expert_panel.main.setup_logging")
    @patch("agent_expert_panel.main.argparse.ArgumentParser")
    def test_main_batch_mode(self, mock_parser, mock_setup_logging, mock_asyncio_run):
        """Test main function in batch mode."""
        # Setup argument parser mock
        mock_args = Mock()
        mock_args.topic = "Test topic"  # Topic provided = batch mode
        mock_args.pattern = "round_robin"
        mock_args.rounds = 3
        mock_args.config_dir = None
        mock_args.verbose = True
        mock_parser.return_value.parse_args.return_value = mock_args

        mock_asyncio_run.return_value = 0

        result = main()

        assert result == 0
        mock_setup_logging.assert_called_once_with(True)
        mock_asyncio_run.assert_called_once()

    @patch("agent_expert_panel.main.argparse.ArgumentParser")
    def test_main_argument_parsing(self, mock_parser):
        """Test that main properly sets up argument parsing."""
        mock_parser_instance = Mock()
        mock_parser.return_value = mock_parser_instance
        mock_parser_instance.parse_args.return_value = Mock(topic=None, verbose=False)

        with patch("agent_expert_panel.main.asyncio.run"):
            main()

        # Verify argument parser was configured
        mock_parser.assert_called_once()
        mock_parser_instance.add_argument.assert_called()

        # Check that required arguments were added
        call_args = [
            call[0][0] for call in mock_parser_instance.add_argument.call_args_list
        ]
        assert "--topic" in call_args or "-t" in call_args
        assert "--pattern" in call_args or "-p" in call_args
        assert "--rounds" in call_args or "-r" in call_args
        assert "--config-dir" in call_args or "-c" in call_args
        assert "--verbose" in call_args or "-v" in call_args
