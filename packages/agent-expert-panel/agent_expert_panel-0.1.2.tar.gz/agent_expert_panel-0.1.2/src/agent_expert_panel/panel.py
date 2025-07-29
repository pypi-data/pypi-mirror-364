"""
Expert Panel Orchestrator

This module provides the main orchestration for running multi-agent expert panel discussions.
Inspired by Microsoft's MAI-DxO and Hugging Face's Consilium approaches to multi-agent collaboration.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.ui import RichConsole
from autogen_agentchat.base import TaskResult

from .agents.create_agent import create_agent
from .models.config import AgentConfig


class DiscussionPattern(Enum):
    """Available discussion patterns for agent interaction."""

    ROUND_ROBIN = "round_robin"
    OPEN_FLOOR = "open_floor"
    STRUCTURED_DEBATE = "structured_debate"


@dataclass
class PanelResult:
    """Results from a panel discussion."""

    topic: str
    discussion_pattern: DiscussionPattern
    agents_participated: List[str]
    discussion_history: List[Dict[str, Any]]
    consensus_reached: bool
    final_recommendation: str
    total_rounds: int


class ExpertPanel:
    """
    Main orchestrator for the 5-agent expert panel discussions.

    The panel consists of:
    - Advocate: Champions ideas with conviction and evidence
    - Critic: Rigorous quality assurance and risk analysis
    - Pragmatist: Practical implementation focus
    - Research Specialist: Fact-finding and evidence gathering
    - Innovator: Creative disruption and breakthrough solutions
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize the expert panel.

        Args:
            config_dir: Directory containing agent configuration files
        """
        self.config_dir = config_dir or Path(__file__).parent.parent.parent / "configs"
        self.agents: Dict[str, AssistantAgent] = {}
        self.logger = logging.getLogger(__name__)

        # Load all agents
        self._load_agents()

    def _load_agents(self) -> None:
        """Load all 5 expert agents from their configuration files."""
        agent_names = [
            "advocate",
            "critic",
            "pragmatist",
            "research_specialist",
            "innovator",
        ]

        for agent_name in agent_names:
            config_file = self.config_dir / f"{agent_name}.yaml"
            if not config_file.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_file}")

            try:
                config = AgentConfig.from_yaml(config_file)
                agent = create_agent(config)
                self.agents[agent_name] = agent
                self.logger.info(f"Loaded {agent_name} agent successfully")
            except Exception as e:
                self.logger.error(f"Failed to load {agent_name} agent: {e}")
                raise

    async def discuss(
        self,
        topic: str,
        pattern: DiscussionPattern = DiscussionPattern.ROUND_ROBIN,
        max_rounds: int = 3,
        participants: Optional[List[str]] = None,
        with_human: bool = False,
    ) -> PanelResult:
        """
        Run a panel discussion on the given topic.

        Args:
            topic: The topic or question for the panel to discuss
            pattern: The discussion pattern to use
            max_rounds: Maximum number of discussion rounds
            participants: Specific agents to include (default: all 5)
            with_human: Whether to include human participant

        Returns:
            PanelResult containing the discussion outcomes
        """
        participants = participants or list(self.agents.keys())
        participating_agents = [self.agents[name] for name in participants]

        self.logger.info(f"Starting panel discussion on: {topic}")
        self.logger.info(f"Pattern: {pattern.value}, Participants: {participants}")

        if pattern == DiscussionPattern.ROUND_ROBIN:
            return await self._run_round_robin_discussion(
                topic, participating_agents, participants, max_rounds
            )
        elif pattern == DiscussionPattern.STRUCTURED_DEBATE:
            return await self._run_structured_debate(
                topic, participating_agents, participants, max_rounds
            )
        else:
            raise NotImplementedError(
                f"Discussion pattern {pattern} not yet implemented"
            )

    async def _run_round_robin_discussion(
        self,
        topic: str,
        agents: List[AssistantAgent],
        agent_names: List[str],
        max_rounds: int,
    ) -> PanelResult:
        """Run a round-robin style discussion."""

        # Create the round-robin group chat
        group_chat = RoundRobinGroupChat(agents, max_turns=max_rounds * len(agents))

        # Create enhanced topic prompt that encourages collaboration
        enhanced_prompt = f"""
        Welcome to the Expert Panel Discussion!
        
        Topic: {topic}
        
        Instructions for the panel:
        - Each expert should provide their unique perspective based on their specialization
        - Build upon or challenge previous speakers' points constructively
        - Aim for a collaborative solution that incorporates diverse viewpoints
        
        Participants:
        """
        for agent in agents:
            enhanced_prompt += f"{agent.name}: {agent.description}\n"

        enhanced_prompt += f"Let's begin the discussion. Each expert will have {max_rounds} opportunities to contribute."

        discussion_history = []

        # Run the discussion using RichConsole for nice output
        task_result: TaskResult = await RichConsole(
            group_chat.run_stream(task=enhanced_prompt)
        )

        # Parse the actual discussion history from the task result
        discussion_history = self._extract_discussion_history(task_result)

        # Extract final recommendation and consensus
        final_recommendation, consensus_reached = self._analyze_discussion_results(
            task_result, agent_names
        )

        # Calculate actual rounds from the discussion
        actual_rounds = self._calculate_discussion_rounds(
            discussion_history, len(agents)
        )

        result = PanelResult(
            topic=topic,
            discussion_pattern=DiscussionPattern.ROUND_ROBIN,
            agents_participated=agent_names,
            discussion_history=discussion_history,
            consensus_reached=consensus_reached,
            final_recommendation=final_recommendation,
            total_rounds=actual_rounds,
        )

        return result

    async def _run_structured_debate(
        self,
        topic: str,
        agents: List[AssistantAgent],
        agent_names: List[str],
        max_rounds: int,
    ) -> PanelResult:
        """Run a structured debate with specific phases."""

        phases = [
            "Initial Position Statements",
            "Evidence and Analysis Phase",
            "Challenge and Rebuttal Phase",
            "Synthesis and Consensus Building",
        ]

        # For structured debate, we'll run the full discussion as one session
        # but structure the prompt to encourage debate phases
        structured_prompt = f"""
        Welcome to the Structured Expert Panel Debate!
        
        Topic: {topic}
        
        This debate will proceed through structured phases:
        1. Initial Position Statements - Each expert states their position
        2. Evidence and Analysis Phase - Present supporting evidence
        3. Challenge and Rebuttal Phase - Challenge other positions
        4. Synthesis and Consensus Building - Work toward agreement
        
        Participants:
        """
        for agent in agents:
            structured_prompt += (
                f"- {agent.name}: {getattr(agent, 'description', 'Expert agent')}\n"
            )

        structured_prompt += (
            f"\nPlease proceed through {len(phases)} structured phases of debate."
        )

        # Create the group chat for structured debate
        group_chat = RoundRobinGroupChat(agents, max_turns=max_rounds * len(agents))

        # Run the structured debate
        task_result: TaskResult = await RichConsole(
            group_chat.run_stream(task=structured_prompt)
        )

        # Parse the discussion history and results
        discussion_history = self._extract_discussion_history(task_result)
        final_recommendation, consensus_reached = self._analyze_discussion_results(
            task_result, agent_names
        )
        actual_rounds = self._calculate_discussion_rounds(
            discussion_history, len(agents)
        )

        result = PanelResult(
            topic=topic,
            discussion_pattern=DiscussionPattern.STRUCTURED_DEBATE,
            agents_participated=agent_names,
            discussion_history=discussion_history,
            consensus_reached=consensus_reached,
            final_recommendation=final_recommendation,
            total_rounds=actual_rounds,
        )

        return result

    def _get_phase_instructions(self, phase_name: str) -> str:
        """Get specific instructions for each debate phase."""
        instructions = {
            "Initial Position Statements": "State your initial position and key arguments",
            "Evidence and Analysis Phase": "Provide supporting evidence and detailed analysis",
            "Challenge and Rebuttal Phase": "Challenge other positions and defend your own",
            "Synthesis and Consensus Building": "Work toward synthesis and common ground",
        }
        return instructions.get(phase_name, "Participate according to your expertise")

    def get_agent_descriptions(self) -> Dict[str, str]:
        """Get descriptions of all agents in the panel."""
        descriptions = {}
        for name, agent in self.agents.items():
            # Get description from config if available, otherwise use agent name
            config_file = self.config_dir / f"{name}.yaml"
            if config_file.exists():
                config = AgentConfig.from_yaml(config_file)
                descriptions[name] = config.description
            else:
                descriptions[name] = f"{name.title()} agent"
        return descriptions

    async def quick_consensus(self, question: str) -> str:
        """
        Get a quick consensus from all agents on a simple question.

        Args:
            question: A straightforward question requiring expert input

        Returns:
            A synthesized response from all experts
        """
        result = await self.discuss(
            topic=question, pattern=DiscussionPattern.ROUND_ROBIN, max_rounds=1
        )
        return result.final_recommendation

    def _extract_discussion_history(
        self, task_result: TaskResult
    ) -> List[Dict[str, Any]]:
        """
        Extract discussion history from the TaskResult.

        Args:
            task_result: The result from the group chat discussion

        Returns:
            List of discussion entries with speaker, content, and metadata
        """
        history = []

        # TaskResult should have messages attribute
        if hasattr(task_result, "messages") and task_result.messages:
            for i, message in enumerate(task_result.messages):
                # Extract speaker and content with multiple fallback approaches
                speaker = None
                content = None

                # Try different message formats
                if hasattr(message, "source"):
                    speaker = message.source
                elif hasattr(message, "name"):
                    speaker = message.name
                elif hasattr(message, "role"):
                    speaker = message.role

                if hasattr(message, "content"):
                    content = message.content
                elif hasattr(message, "text"):
                    content = message.text
                else:
                    content = str(message)

                # Use fallback names if needed
                if not speaker:
                    speaker = f"Agent_{i}"

                # Skip empty messages and system messages
                if content and content.strip() and not content.startswith("System:"):
                    history.append(
                        {
                            "round": i + 1,
                            "speaker": speaker,
                            "content": content.strip(),
                            "timestamp": getattr(message, "timestamp", None),
                        }
                    )

        # If messages aren't available, try other attributes
        elif hasattr(task_result, "chat_history"):
            # Some versions might have chat_history
            for i, entry in enumerate(task_result.chat_history):
                history.append(
                    {
                        "round": i + 1,
                        "speaker": entry.get("name", f"Agent_{i}"),
                        "content": entry.get("content", str(entry)),
                        "timestamp": entry.get("timestamp", None),
                    }
                )

        # Fallback: Try to parse from string representation of task_result
        elif hasattr(task_result, "__str__"):
            try:
                # If TaskResult can be converted to string, try to parse it
                result_str = str(task_result)
                if len(result_str) > 50:  # Only if there's substantial content
                    history.append(
                        {
                            "round": 1,
                            "speaker": "Panel Discussion",
                            "content": result_str,
                            "timestamp": None,
                        }
                    )
            except Exception as e:
                self.logger.warning(
                    f"Could not parse TaskResult string representation: {e}"
                )

        # Log the extraction results for debugging
        self.logger.debug(
            f"Extracted {len(history)} discussion entries from TaskResult"
        )
        if not history:
            self.logger.warning(
                "No discussion history could be extracted from TaskResult"
            )

        return history

    def _analyze_discussion_results(
        self, task_result: TaskResult, agent_names: List[str]
    ) -> Tuple[str, bool]:
        """
        Analyze the discussion results to extract final recommendation and consensus.

        Args:
            task_result: The result from the group chat discussion
            agent_names: List of participating agent names

        Returns:
            Tuple of (final_recommendation, consensus_reached)
        """
        # Initialize defaults
        final_recommendation = (
            "Discussion completed - see individual agent responses above."
        )
        consensus_reached = False

        try:
            if hasattr(task_result, "messages") and task_result.messages:
                # Get all messages with content
                all_messages = []
                for msg in task_result.messages:
                    content = None
                    speaker = None

                    # Extract content using multiple approaches
                    if hasattr(msg, "content"):
                        content = msg.content
                    elif hasattr(msg, "text"):
                        content = msg.text
                    else:
                        content = str(msg)

                    # Extract speaker
                    if hasattr(msg, "source"):
                        speaker = msg.source
                    elif hasattr(msg, "name"):
                        speaker = msg.name
                    elif hasattr(msg, "role"):
                        speaker = msg.role

                    if content and content.strip():
                        all_messages.append(
                            {
                                "speaker": speaker or "Unknown",
                                "content": content.strip(),
                            }
                        )

                if all_messages:
                    # Analyze consensus by looking for agreement patterns
                    consensus_reached = self._detect_consensus(all_messages)

                    # Create a comprehensive final recommendation
                    final_recommendation = self._synthesize_recommendation(
                        all_messages, agent_names
                    )

            # Fallback: get summary from task result if available
            elif hasattr(task_result, "summary") and task_result.summary:
                final_recommendation = task_result.summary
                consensus_reached = True  # Assume consensus if there's a summary

        except Exception as e:
            self.logger.error(f"Error analyzing discussion results: {e}")
            # Keep the default values

        return final_recommendation, consensus_reached

    def _calculate_discussion_rounds(
        self, discussion_history: List[Dict[str, Any]], num_agents: int
    ) -> int:
        """
        Calculate the number of discussion rounds based on the history.

        Args:
            discussion_history: List of discussion entries
            num_agents: Number of participating agents

        Returns:
            Number of complete discussion rounds
        """
        if not discussion_history or num_agents == 0:
            return 0

        # Simple calculation: total messages divided by number of agents
        # This gives an approximate number of rounds
        return max(1, len(discussion_history) // num_agents)

    def _detect_consensus(self, messages: List[Dict[str, str]]) -> bool:
        """
        Detect if consensus was reached in the discussion.

        Args:
            messages: List of message dictionaries with speaker and content

        Returns:
            True if consensus appears to have been reached
        """
        if len(messages) < 2:
            return False

        # Keywords that suggest agreement or consensus
        agreement_keywords = [
            "agree",
            "consensus",
            "recommend",
            "conclusion",
            "therefore",
            "in summary",
            "overall",
            "final recommendation",
            "we conclude",
            "i support",
            "good point",
            "excellent idea",
            "building on",
            "i concur",
            "that makes sense",
            "sounds reasonable",
        ]

        # Keywords that suggest disagreement
        disagreement_keywords = [
            "disagree",
            "however",
            "but",
            "on the other hand",
            "i think otherwise",
            "that's not right",
            "i object",
            "i challenge",
            "problem",
            "problems",
            "concerned about",
            "risk is",
            "major flaw",
            "flawed",
            "wrong",
        ]

        agreement_count = 0
        disagreement_count = 0

        # Analyze the last few messages for consensus indicators
        recent_messages = messages[-min(5, len(messages)) :]

        for msg in recent_messages:
            content_lower = msg["content"].lower()

            # Count agreement indicators
            for keyword in agreement_keywords:
                if keyword in content_lower:
                    agreement_count += 1
                    break

            # Count disagreement indicators
            for keyword in disagreement_keywords:
                if keyword in content_lower:
                    disagreement_count += 1
                    break

        # Consensus if more agreement than disagreement
        return (
            agreement_count > disagreement_count
            and agreement_count >= len(recent_messages) // 2
        )

    def _synthesize_recommendation(
        self, messages: List[Dict[str, str]], agent_names: List[str]
    ) -> str:
        """
        Synthesize a final recommendation from all agent messages.

        Args:
            messages: List of message dictionaries with speaker and content
            agent_names: List of participating agent names

        Returns:
            Synthesized final recommendation
        """
        if not messages:
            return "No discussion content available."

        # If there's only one message or the last message is comprehensive, use it
        if len(messages) == 1 or len(messages[-1]["content"]) > 200:
            return f"Final Panel Recommendation:\n\n{messages[-1]['content']}"

        # Group messages by agent
        agent_contributions = {}
        for msg in messages:
            speaker = msg["speaker"]
            if speaker not in agent_contributions:
                agent_contributions[speaker] = []
            agent_contributions[speaker].append(msg["content"])

        # Create a structured summary
        recommendation = "## Expert Panel Final Recommendation\n\n"

        # Add contributions from each agent
        for agent_name in agent_names:
            if agent_name in agent_contributions:
                contributions = agent_contributions[agent_name]
                # Use the last (most recent) contribution from each agent
                latest_contribution = contributions[-1]

                # Truncate very long contributions
                if len(latest_contribution) > 300:
                    latest_contribution = latest_contribution[:300] + "..."

                recommendation += f"**{agent_name.title()}:** {latest_contribution}\n\n"

        # Add any unmatched contributors
        for speaker, contributions in agent_contributions.items():
            if speaker.lower() not in [name.lower() for name in agent_names]:
                latest_contribution = contributions[-1]
                if len(latest_contribution) > 300:
                    latest_contribution = latest_contribution[:300] + "..."
                recommendation += f"**{speaker}:** {latest_contribution}\n\n"

        # If the recommendation is too short, add the last few messages
        if len(recommendation) < 200 and len(messages) > 1:
            recommendation += "\n**Summary of Recent Discussion:**\n"
            for msg in messages[-3:]:  # Last 3 messages
                content = (
                    msg["content"][:200] + "..."
                    if len(msg["content"]) > 200
                    else msg["content"]
                )
                recommendation += f"- {msg['speaker']}: {content}\n"

        return recommendation
