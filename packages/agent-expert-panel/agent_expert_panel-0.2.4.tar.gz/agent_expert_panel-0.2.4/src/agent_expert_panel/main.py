#!/usr/bin/env python3
"""
Agent Expert Panel - Main CLI Interface

Run multi-agent expert panel discussions from the command line.
Inspired by Microsoft's MAI-DxO and Hugging Face's Consilium.
"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, List
from enum import Enum

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel as RichPanel
from rich.markdown import Markdown

from agent_expert_panel.panel import ExpertPanel, DiscussionPattern


# Create the main Typer app
app = typer.Typer(
    name="agent-panel",
    help="🧠 Agent Expert Panel - Multi-agent discussion system",
    epilog="""
Examples:

  🎯 Interactive mode (includes option for human participation):
  $ agent-panel

  🤖 Batch mode:
  $ agent-panel discuss "Should we adopt microservices architecture?" --pattern round-robin --rounds 3

  👥 Batch mode with human participation:
  $ agent-panel discuss "Product roadmap planning" --pattern structured-debate --rounds 2 --with-human

  ⚙️ With custom config directory:
  $ agent-panel discuss "AI ethics in healthcare" --config-dir ./my-configs

  📋 List available agents:
  $ agent-panel list-agents

  ℹ️ Show agent details:
  $ agent-panel show-agent advocate
    """,
    rich_markup_mode="rich",
    no_args_is_help=False,  # Allow running without args for interactive mode
)


class DiscussionPatternEnum(str, Enum):
    """Discussion patterns available for the panel."""

    round_robin = "round-robin"
    structured_debate = "structured-debate"
    open_floor = "open-floor"


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def display_welcome() -> None:
    """Display welcome message and panel overview."""
    console = Console()

    welcome_text = """
    # 🧠 Agent Expert Panel

    Welcome to the multi-agent expert panel discussion system!

    **Your Expert Panel consists of:**
    - 🥊 **Advocate**: Champions ideas with conviction and evidence
    - 🔍 **Critic**: Rigorous quality assurance and risk analysis
    - ⚡ **Pragmatist**: Practical implementation focus
    - 📚 **Research Specialist**: Fact-finding and evidence gathering
    - 💡 **Innovator**: Creative disruption and breakthrough solutions

    These AI experts will collaborate to provide comprehensive insights on your topics.
    """

    console.print(
        RichPanel(Markdown(welcome_text), title="Welcome", border_style="blue")
    )


def display_agents(panel: ExpertPanel) -> None:
    """Display information about available agents."""
    console = Console()

    table = Table(title="Available Experts")
    table.add_column("Expert", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Description", style="white")

    descriptions = panel.get_agent_descriptions()

    roles = {
        "advocate": "🥊 Champion",
        "critic": "🔍 Quality Assurance",
        "pragmatist": "⚡ Implementation",
        "research_specialist": "📚 Research & Evidence",
        "innovator": "💡 Creative Disruption",
    }

    for agent_name, description in descriptions.items():
        role = roles.get(agent_name, "Expert")
        table.add_row(
            agent_name.title(),
            role,
            description[:80] + "..." if len(description) > 80 else description,
        )

    console.print(table)


async def interactive_mode() -> int:
    """Run in interactive mode with prompts."""
    console = Console()
    display_welcome()

    try:
        # Initialize the panel
        console.print("\n[yellow]Initializing expert panel...[/yellow]")
        panel = ExpertPanel()
        console.print("[green]✓ Expert panel ready![/green]\n")

        # Show available agents
        if Confirm.ask("Would you like to see the expert panel details?", default=True):
            display_agents(panel)
            console.print()

        while True:
            # Get topic from user
            topic = Prompt.ask(
                "\n[bold cyan]What topic would you like the experts to discuss?[/bold cyan]"
            )

            if topic.lower() in ["quit", "exit", "q"]:
                break

            # Choose discussion pattern
            console.print("\n[yellow]Available discussion patterns:[/yellow]")
            patterns = list(DiscussionPattern)
            for i, pattern in enumerate(patterns, 1):
                console.print(f"  {i}. {pattern.value.replace('_', ' ').title()}")

            pattern_choice = Prompt.ask(
                "Choose discussion pattern",
                choices=[str(i) for i in range(1, len(patterns) + 1)],
                default="1",
            )
            selected_pattern = patterns[int(pattern_choice) - 1]

            # Get max rounds
            max_rounds = int(Prompt.ask("Maximum discussion rounds", default="3"))

            # Ask if human wants to participate
            include_human = Confirm.ask(
                "Would you like to participate in the discussion as a human expert?",
                default=False,
            )

            # Run discussion
            if include_human:
                console.print(
                    f"\n[green]Starting {selected_pattern.value.replace('_', ' ')} discussion with human participation...[/green]\n"
                )
                console.print(
                    "[yellow]You will be prompted for input during your turns in the discussion.[/yellow]\n"
                )

                result = await panel.discuss(
                    topic=topic,
                    pattern=selected_pattern,
                    max_rounds=max_rounds,
                    with_human=True,
                    human_name="Human Expert",
                )
            else:
                console.print(
                    f"\n[green]Starting {selected_pattern.value.replace('_', ' ')} discussion...[/green]\n"
                )

                result = await panel.discuss(
                    topic=topic, pattern=selected_pattern, max_rounds=max_rounds
                )

            # Display results
            console.print(
                RichPanel(
                    f"[bold]Topic:[/bold] {result.topic}\n"
                    f"[bold]Pattern:[/bold] {result.discussion_pattern.value}\n"
                    f"[bold]Participants:[/bold] {', '.join(result.agents_participated)}\n"
                    f"[bold]Rounds:[/bold] {result.total_rounds}\n"
                    f"[bold]Consensus:[/bold] {'✓ Yes' if result.consensus_reached else '✗ No'}\n\n"
                    f"[bold]Final Recommendation:[/bold]\n{result.final_recommendation}",
                    title="Discussion Results",
                    border_style="green",
                )
            )

            if not Confirm.ask(
                "\nWould you like to discuss another topic?", default=True
            ):
                break

    except KeyboardInterrupt:
        console.print("\n[yellow]Discussion interrupted by user.[/yellow]")
        return 1
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return 1

    console.print("\n[blue]Thank you for using Agent Expert Panel![/blue]")
    return 0


@app.command()
def discuss(
    topic: str = typer.Argument(..., help="Topic for the expert panel to discuss"),
    pattern: DiscussionPatternEnum = typer.Option(
        DiscussionPatternEnum.round_robin,
        "--pattern",
        "-p",
        help="Discussion pattern to use",
    ),
    rounds: int = typer.Option(
        3, "--rounds", "-r", help="Maximum number of discussion rounds", min=1, max=10
    ),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    with_human: bool = typer.Option(
        False,
        "--with-human/--no-human",
        help="Include human participation in the discussion",
    ),
    participants: Optional[List[str]] = typer.Option(
        None,
        "--participants",
        help="Specific agents to include (e.g., --participants advocate --participants critic)",
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    🎯 Run a panel discussion on a specific topic.

    This command runs a single discussion in batch mode with the specified parameters.
    Perfect for automation, scripting, or when you know exactly what you want to discuss.
    """

    async def run_discussion():
        console = Console()

        # Setup logging
        setup_logging(verbose)

        try:
            # Parse pattern
            discussion_pattern = DiscussionPattern(pattern.value.replace("-", "_"))

            # Initialize panel
            console.print("[yellow]Initializing expert panel...[/yellow]")
            panel = ExpertPanel(config_dir=config_dir)
            console.print("[green]✓ Expert panel ready![/green]\n")

            # Run discussion
            if with_human:
                console.print(
                    f"[green]Starting discussion on: {topic} (with human participation)[/green]\n"
                )
                console.print(
                    "[yellow]You will be prompted for input during your turns in the discussion.[/yellow]\n"
                )

                result = await panel.discuss(
                    topic=topic,
                    pattern=discussion_pattern,
                    max_rounds=rounds,
                    participants=participants,
                    with_human=True,
                    human_name="Human Expert",
                )
            else:
                console.print(f"[green]Starting discussion on: {topic}[/green]\n")

                result = await panel.discuss(
                    topic=topic,
                    pattern=discussion_pattern,
                    max_rounds=rounds,
                    participants=participants,
                )

            # Output results
            console.print(
                RichPanel(
                    f"[bold]Topic:[/bold] {result.topic}\n"
                    f"[bold]Pattern:[/bold] {result.discussion_pattern.value}\n"
                    f"[bold]Participants:[/bold] {', '.join(result.agents_participated)}\n"
                    f"[bold]Rounds:[/bold] {result.total_rounds}\n"
                    f"[bold]Consensus:[/bold] {'✓ Yes' if result.consensus_reached else '✗ No'}\n\n"
                    f"[bold]Final Recommendation:[/bold]\n{result.final_recommendation}",
                    title="Discussion Results",
                    border_style="green",
                )
            )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_discussion())


@app.command("list-agents")
def list_agents(
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    📋 List all available expert agents and their roles.

    Shows a detailed table of all expert agents in the panel,
    including their names, roles, and descriptions.
    """
    console = Console()

    # Setup logging
    setup_logging(verbose)

    try:
        # Initialize panel
        if config_dir:
            console.print(
                f"[yellow]Loading expert panel from custom config directory: {config_dir}[/yellow]"
            )
        else:
            console.print("[yellow]Loading expert panel...[/yellow]")
        panel = ExpertPanel(config_dir=config_dir)
        console.print("[green]✓ Expert panel loaded![/green]\n")

        # Display agents
        display_agents(panel)

    except Exception as e:
        console.print(f"[red]Error loading agents: {e}[/red]")
        raise typer.Exit(1)


@app.command("show-agent")
def show_agent(
    agent_name: str = typer.Argument(..., help="Name of the agent to show details for"),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    ℹ️ Show detailed information about a specific expert agent.

    Displays comprehensive details about an agent including its configuration,
    role, and capabilities.
    """
    console = Console()

    # Setup logging
    setup_logging(verbose)

    try:
        # Initialize panel
        if config_dir:
            console.print(
                f"[yellow]Loading expert panel from custom config directory: {config_dir}[/yellow]"
            )
        else:
            console.print("[yellow]Loading expert panel...[/yellow]")
        panel = ExpertPanel(config_dir=config_dir)

        # Get agent descriptions
        descriptions = panel.get_agent_descriptions()

        if agent_name.lower() not in descriptions:
            available_agents = ", ".join(descriptions.keys())
            console.print(f"[red]Agent '{agent_name}' not found.[/red]")
            console.print(f"[yellow]Available agents: {available_agents}[/yellow]")
            raise typer.Exit(1)

        # Display agent details
        agent_desc = descriptions[agent_name.lower()]

        roles = {
            "advocate": "🥊 Champion",
            "critic": "🔍 Quality Assurance",
            "pragmatist": "⚡ Implementation",
            "research_specialist": "📚 Research & Evidence",
            "innovator": "💡 Creative Disruption",
        }

        role = roles.get(agent_name.lower(), "Expert")

        console.print(
            RichPanel(
                f"[bold]Name:[/bold] {agent_name.title()}\n"
                f"[bold]Role:[/bold] {role}\n\n"
                f"[bold]Description:[/bold]\n{agent_desc}",
                title=f"Agent Details: {agent_name.title()}",
                border_style="cyan",
            )
        )

    except Exception as e:
        console.print(f"[red]Error loading agent details: {e}[/red]")
        raise typer.Exit(1)


@app.command("quick-consensus")
def quick_consensus(
    question: str = typer.Argument(..., help="Question to get quick consensus on"),
    config_dir: Optional[Path] = typer.Option(
        None,
        "--config-dir",
        "-c",
        help="Directory containing agent configuration files",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    ⚡ Get a quick consensus from all experts on a simple question.

    Runs a single round of discussion to get rapid input from all experts
    on a straightforward question or decision.
    """

    async def run_quick_consensus():
        console = Console()

        # Setup logging
        setup_logging(verbose)

        try:
            # Initialize panel
            console.print("[yellow]Initializing expert panel...[/yellow]")
            panel = ExpertPanel(config_dir=config_dir)
            console.print("[green]✓ Expert panel ready![/green]\n")

            console.print(f"[green]Getting quick consensus on: {question}[/green]\n")

            # Get consensus
            result = await panel.quick_consensus(question)

            # Display result
            console.print(
                RichPanel(
                    result,
                    title="Quick Consensus",
                    border_style="green",
                )
            )

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise typer.Exit(1)

    asyncio.run(run_quick_consensus())


@app.command("validate-config")
def validate_config(
    config_dir: Path = typer.Argument(
        ...,
        help="Directory containing agent configuration files to validate",
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    🔍 Validate a directory of agent configuration files.

    Checks that all required agent configuration files exist, are valid YAML,
    and contain the necessary fields for the expert panel to function.
    """
    console = Console()
    setup_logging(verbose)

    console.print(
        f"[yellow]Validating configuration directory: {config_dir}[/yellow]\n"
    )

    required_agents = [
        "advocate",
        "critic",
        "pragmatist",
        "research_specialist",
        "innovator",
    ]
    required_fields = ["name", "model_name", "description", "system_message"]

    errors = []
    warnings = []
    valid_configs = 0

    for agent_name in required_agents:
        config_file = config_dir / f"{agent_name}.yaml"

        # Check if file exists
        if not config_file.exists():
            errors.append(f"❌ Missing configuration file: {config_file}")
            continue

        # Check if file is readable
        if not config_file.is_file():
            errors.append(f"❌ Not a file: {config_file}")
            continue

        try:
            # Try to parse YAML
            import yaml

            with open(config_file, "r") as f:
                config_data = yaml.safe_load(f)

            if not isinstance(config_data, dict):
                errors.append(f"❌ {agent_name}.yaml: Not a valid YAML dictionary")
                continue

            # Check required fields
            missing_fields = []
            for field in required_fields:
                if field not in config_data:
                    missing_fields.append(field)
                elif not config_data[field]:
                    missing_fields.append(f"{field} (empty)")

            if missing_fields:
                errors.append(
                    f"❌ {agent_name}.yaml: Missing required fields: {', '.join(missing_fields)}"
                )
                continue

            # Check name matches filename
            if config_data.get("name") != agent_name:
                warnings.append(
                    f"⚠️  {agent_name}.yaml: Name field '{config_data.get('name')}' doesn't match filename"
                )

            # Try to load as AgentConfig
            try:
                from agent_expert_panel.models.config import AgentConfig

                _ = AgentConfig.from_yaml(config_file)
                console.print(f"✅ {agent_name}.yaml: Valid configuration")
                valid_configs += 1
            except Exception as e:
                errors.append(
                    f"❌ {agent_name}.yaml: Failed to load as AgentConfig: {e}"
                )

        except yaml.YAMLError as e:
            errors.append(f"❌ {agent_name}.yaml: Invalid YAML syntax: {e}")
        except Exception as e:
            errors.append(f"❌ {agent_name}.yaml: Error reading file: {e}")

    # Display summary
    console.print("\n[bold]Validation Summary:[/bold]")
    console.print(f"✅ Valid configurations: {valid_configs}/{len(required_agents)}")

    if warnings:
        console.print(f"\n[yellow]Warnings ({len(warnings)}):[/yellow]")
        for warning in warnings:
            console.print(f"  {warning}")

    if errors:
        console.print(f"\n[red]Errors ({len(errors)}):[/red]")
        for error in errors:
            console.print(f"  {error}")

        console.print(
            "\n[red]❌ Configuration directory is not valid for use with agent-panel[/red]"
        )
        raise typer.Exit(1)
    else:
        console.print(
            "\n[green]🎉 Configuration directory is valid and ready to use![/green]"
        )
        console.print(
            f"\n[dim]Usage: agent-panel list-agents --config-dir {config_dir}[/dim]"
        )


@app.callback()
def main(
    ctx: typer.Context,
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging"
    ),
) -> None:
    """
    🧠 Agent Expert Panel - Multi-agent discussion system

    A sophisticated multi-agent discussion framework that orchestrates AI experts
    to solve complex problems through collaborative reasoning.

    Run without any commands to start interactive mode, or use specific commands
    for batch operations.
    """
    # Setup logging
    setup_logging(verbose)

    # If no command is provided, run interactive mode
    if ctx.invoked_subcommand is None:
        result = asyncio.run(interactive_mode())
        raise typer.Exit(result)


if __name__ == "__main__":
    app()
