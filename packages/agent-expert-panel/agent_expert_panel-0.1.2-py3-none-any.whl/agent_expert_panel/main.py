#!/usr/bin/env python3
"""
Agent Expert Panel - Main CLI Interface

Run multi-agent expert panel discussions from the command line.
Inspired by Microsoft's MAI-DxO and Hugging Face's Consilium.
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel as RichPanel
from rich.markdown import Markdown

from src.agent_expert_panel.panel import ExpertPanel, DiscussionPattern


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


async def interactive_mode() -> None:
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

            # Run discussion
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
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        return 1

    console.print("\n[blue]Thank you for using Agent Expert Panel![/blue]")
    return 0


async def batch_mode(
    topic: str, pattern: str, max_rounds: int, config_dir: Path = None
) -> int:
    """Run a single discussion in batch mode."""
    console = Console()

    try:
        # Parse pattern
        try:
            discussion_pattern = DiscussionPattern(pattern.lower())
        except ValueError:
            console.print(
                f"[red]Error: Invalid pattern '{pattern}'. Available: {[p.value for p in DiscussionPattern]}[/red]"
            )
            return 1

        # Initialize panel
        console.print("[yellow]Initializing expert panel...[/yellow]")
        panel = ExpertPanel(config_dir=config_dir)
        console.print("[green]✓ Expert panel ready![/green]\n")

        # Run discussion
        console.print(f"[green]Starting discussion on: {topic}[/green]\n")

        result = await panel.discuss(
            topic=topic, pattern=discussion_pattern, max_rounds=max_rounds
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

        return 0

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Expert Panel - Multi-agent discussion system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python main.py
  
  # Batch mode
  python main.py --topic "Should we adopt microservices architecture?" --pattern round_robin --rounds 3
  
  # With custom config directory
  python main.py --config-dir ./my-configs --topic "AI ethics in healthcare"
        """,
    )

    parser.add_argument("--topic", "-t", help="Topic for the expert panel to discuss")

    parser.add_argument(
        "--pattern",
        "-p",
        choices=[p.value for p in DiscussionPattern],
        default="round_robin",
        help="Discussion pattern to use (default: round_robin)",
    )

    parser.add_argument(
        "--rounds",
        "-r",
        type=int,
        default=3,
        help="Maximum number of discussion rounds (default: 3)",
    )

    parser.add_argument(
        "--config-dir",
        "-c",
        type=Path,
        help="Directory containing agent configuration files",
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Run in appropriate mode
    if args.topic:
        # Batch mode
        return asyncio.run(
            batch_mode(args.topic, args.pattern, args.rounds, args.config_dir)
        )
    else:
        # Interactive mode
        return asyncio.run(interactive_mode())


if __name__ == "__main__":
    sys.exit(main())
