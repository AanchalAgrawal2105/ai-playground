"""
Command-Line Interface for Airflow Intelligence Agent

This module provides a beautiful, user-friendly CLI for interacting with
the AI agent. It supports multiple modes and rich terminal output.

Usage:
    python -m agents.airflow_intelligence.cli interactive
    python -m agents.airflow_intelligence.cli mission "Find slow pipelines"
    python -m agents.airflow_intelligence.cli report
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
if _env_path.exists():
    load_dotenv(_env_path)
else:
    load_dotenv()

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  Rich library not installed. Install with: uv pip install rich")
    print("   Falling back to basic output.\n")

from ..core import create_orchestrator, AgentOrchestrator

# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Only show warnings/errors in CLI
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentCLI:
    """
    Command-line interface for the Airflow Intelligence Agent.
    """

    def __init__(self):
        """Initialize CLI."""
        if RICH_AVAILABLE:
            self.console = Console()
        else:
            self.console = None
        self.orchestrator: Optional[AgentOrchestrator] = None

    def print(self, *args, **kwargs):
        """Print with Rich if available, else standard print."""
        if self.console:
            self.console.print(*args, **kwargs)
        else:
            print(*args, **kwargs)

    def print_banner(self):
        """Print welcome banner."""
        if self.console:
            banner = """
# 🤖 Airflow Intelligence Agent

**Autonomous AI for Pipeline Monitoring**

Powered by Claude AI + AWS Bedrock
            """
            panel = Panel(
                Markdown(banner),
                border_style="cyan",
                box=box.DOUBLE
            )
            self.console.print(panel)
        else:
            print("="*80)
            print("🤖 Airflow Intelligence Agent")
            print("Autonomous AI for Pipeline Monitoring")
            print("="*80 + "\n")

    def initialize_orchestrator(self) -> bool:
        """
        Initialize the orchestrator with configuration.

        Returns:
            True if successful, False otherwise
        """
        try:
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Initializing agent...", total=None)
                    self.orchestrator = create_orchestrator()
                    progress.update(task, completed=True)
            else:
                print("Initializing agent...")
                self.orchestrator = create_orchestrator()
                print("✅ Agent initialized\n")

            return True

        except ValueError as e:
            self.print(f"\n[bold red]❌ Configuration Error:[/bold red] {e}\n")
            self.print("[yellow]💡 Tip:[/yellow] Make sure your .env file is configured correctly.")
            self.print("   Required: AIRFLOW_DB_URL")
            self.print("   Optional: AWS credentials, SLACK_BOT_TOKEN\n")
            return False

        except Exception as e:
            self.print(f"\n[bold red]❌ Initialization Error:[/bold red] {e}\n")
            logger.error(f"Orchestrator initialization failed: {e}", exc_info=True)
            return False

    def show_config(self):
        """Display current configuration."""
        if not self.orchestrator:
            self.print("[red]Orchestrator not initialized[/red]")
            return

        config = self.orchestrator.config

        if self.console:
            table = Table(title="Configuration", box=box.ROUNDED)
            table.add_column("Setting", style="cyan", no_wrap=True)
            table.add_column("Value", style="green")

            table.add_row("Model", config.model_id)
            table.add_row("Region", config.aws_region)
            table.add_row("Temperature", str(config.temperature))
            table.add_row("Database", "✅ Connected")
            table.add_row("Slack", "✅ Enabled" if config.enable_slack else "❌ Disabled")
            table.add_row("Anomaly Threshold", f"{config.anomaly_multiplier}x")

            self.console.print(table)
        else:
            print("\nConfiguration:")
            print(f"  Model: {config.model_id}")
            print(f"  Region: {config.aws_region}")
            print(f"  Database: Connected")
            print(f"  Slack: {'Enabled' if config.enable_slack else 'Disabled'}")
            print()

    def cmd_interactive(self):
        """Run interactive chat mode."""
        self.print_banner()

        if not self.initialize_orchestrator():
            return 1

        self.print("\n[bold green]Interactive Mode Started[/bold green]\n")
        self.print("[dim]Type 'help' for commands, 'exit' to quit[/dim]\n")

        # Run interactive mode
        try:
            self.orchestrator.interactive_mode()
            return 0
        except KeyboardInterrupt:
            self.print("\n\n👋 Goodbye!")
            return 0
        except Exception as e:
            self.print(f"\n[bold red]Error:[/bold red] {e}")
            logger.error(f"Interactive mode error: {e}", exc_info=True)
            return 1

    def cmd_mission(self, objective: str, verbose: bool = False):
        """
        Execute a single mission.

        Args:
            objective: The objective for the agent
            verbose: Show detailed reasoning
        """
        self.print_banner()

        if not self.initialize_orchestrator():
            return 1

        self.print(f"\n[bold cyan]🎯 Mission:[/bold cyan] {objective}\n")

        try:
            result = self.orchestrator.execute_mission(
                objective=objective,
                show_reasoning=verbose,
                return_details=True
            )

            if result["success"]:
                # Display response
                if self.console:
                    self.console.print("\n[bold green]🤖 Agent Response:[/bold green]\n")
                    self.console.print(Markdown(result["response"]))

                    # Show execution details
                    if verbose:
                        self.console.print("\n[dim]─" * 40 + "[/dim]")
                        self.console.print(f"[dim]Iterations: {result.get('iterations', 0)}[/dim]")
                        self.console.print(f"[dim]Tools used: {len(result.get('tools_used', []))}[/dim]")
                else:
                    print("\n🤖 Agent Response:")
                    print(result["response"])
                    if verbose:
                        print(f"\nIterations: {result.get('iterations', 0)}")
                        print(f"Tools used: {len(result.get('tools_used', []))}")

                return 0
            else:
                self.print(f"\n[bold red]❌ Mission Failed:[/bold red] {result.get('error', 'Unknown error')}")
                return 1

        except Exception as e:
            self.print(f"\n[bold red]❌ Error:[/bold red] {e}")
            logger.error(f"Mission execution error: {e}", exc_info=True)
            return 1

    def cmd_report(self):
        """Generate automated monitoring report."""
        self.print_banner()

        # Initialize orchestrator with higher iteration limit for comprehensive reports
        try:
            if self.console:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console
                ) as progress:
                    task = progress.add_task("Initializing agent...", total=None)
                    self.orchestrator = create_orchestrator(max_iterations=20)  # Higher limit for reports
                    progress.update(task, completed=True)
            else:
                print("Initializing agent (configured for comprehensive reports)...")
                self.orchestrator = create_orchestrator(max_iterations=20)
                print("✅ Agent initialized\n")

        except ValueError as e:
            self.print(f"\n[bold red]❌ Configuration Error:[/bold red] {e}\n")
            return 1
        except Exception as e:
            self.print(f"\n[bold red]❌ Initialization Error:[/bold red] {e}\n")
            return 1

        self.print("\n[bold cyan]📊 Generating Monitoring Report[/bold cyan]\n")

        try:
            result = self.orchestrator.generate_report()

            if result["success"]:
                if self.console:
                    self.console.print("\n[bold green]✅ Report Generated[/bold green]\n")
                    self.console.print(Markdown(result["response"]))

                    # Summary
                    self.console.print("\n[dim]─" * 40 + "[/dim]")
                    self.console.print(f"[dim]Timestamp: {result.get('timestamp', 'N/A')}[/dim]")
                    self.console.print(f"[dim]Tools used: {len(result.get('tools_used', []))}[/dim]")
                    self.console.print(f"[dim]Iterations: {result.get('iterations', 'N/A')}[/dim]")
                else:
                    print("\n✅ Report Generated\n")
                    print(result["response"])

                return 0
            else:
                self.print(f"\n[bold red]❌ Report Generation Failed:[/bold red] {result.get('error', 'Unknown error')}")
                return 1

        except Exception as e:
            self.print(f"\n[bold red]❌ Error:[/bold red] {e}")
            logger.error(f"Report generation error: {e}", exc_info=True)
            return 1

    def cmd_config(self):
        """Display configuration."""
        self.print_banner()

        if not self.initialize_orchestrator():
            return 1

        self.show_config()
        return 0

    def cmd_proactive(self, interval: int = 15):
        """
        Run proactive monitoring mode.

        Agent runs continuously and autonomously decides when to investigate and alert.

        Args:
            interval: Check interval in minutes (default: 15)
        """
        self.print_banner()

        self.print("\n[bold cyan]🤖 Starting Proactive Monitoring Mode[/bold cyan]\n")
        self.print(f"[dim]Check interval: {interval} minutes[/dim]")
        self.print(f"[dim]Agent will run continuously and decide autonomously when to alert[/dim]\n")

        try:
            from ..monitoring import ProactiveMonitor
            from ..core import AgentConfig

            # Load config
            config = AgentConfig.from_env()

            # Validate config
            errors = config.validate()
            if errors:
                self.print(f"[bold red]❌ Configuration Error:[/bold red]")
                for error in errors:
                    self.print(f"   • {error}")
                return 1

            # Create and start monitor
            monitor = ProactiveMonitor(config, check_interval_minutes=interval)
            monitor.start()

            return 0

        except KeyboardInterrupt:
            self.print("\n\n👋 Monitoring stopped by user")
            return 0
        except Exception as e:
            self.print(f"\n[bold red]❌ Error:[/bold red] {e}")
            logger.error(f"Proactive monitoring error: {e}", exc_info=True)
            return 1

    def cmd_test(self):
        """Test agent connectivity and basic functionality."""
        self.print_banner()
        self.print("\n[bold cyan]🧪 Running System Tests[/bold cyan]\n")

        if not self.initialize_orchestrator():
            return 1

        tests_passed = 0
        tests_total = 3

        # Test 1: Configuration
        self.print("1. Testing configuration... ", end="")
        try:
            errors = self.orchestrator.config.validate()
            if not errors:
                self.print("[green]✓ PASS[/green]")
                tests_passed += 1
            else:
                self.print(f"[red]✗ FAIL[/red]: {errors}")
        except Exception as e:
            self.print(f"[red]✗ FAIL[/red]: {e}")

        # Test 2: Database connectivity
        self.print("2. Testing database connection... ", end="")
        try:
            # Try a simple query
            result = self.orchestrator.tool_registry.db_tools.get_dag_health_summary()
            if result and not result.get("error"):
                self.print("[green]✓ PASS[/green]")
                tests_passed += 1
            else:
                self.print(f"[red]✗ FAIL[/red]: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.print(f"[red]✗ FAIL[/red]: {e}")

        # Test 3: Agent reasoning
        self.print("3. Testing agent reasoning... ", end="")
        try:
            # Simple test mission
            result = self.orchestrator.execute_mission(
                objective="Say 'test successful' if you can read this",
                show_reasoning=False
            )
            if result["success"]:
                self.print("[green]✓ PASS[/green]")
                tests_passed += 1
            else:
                self.print(f"[red]✗ FAIL[/red]: {result.get('error', 'Unknown error')}")
        except Exception as e:
            self.print(f"[red]✗ FAIL[/red]: {e}")

        # Summary
        self.print(f"\n[bold]Results: {tests_passed}/{tests_total} tests passed[/bold]")

        if tests_passed == tests_total:
            self.print("\n[bold green]✅ All tests passed! System ready.[/bold green]")
            return 0
        else:
            self.print("\n[bold yellow]⚠️  Some tests failed. Check configuration.[/bold yellow]")
            return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Airflow Intelligence Agent - Autonomous AI for pipeline monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive chat mode
  %(prog)s interactive

  # Execute a mission
  %(prog)s mission "Find performance anomalies in last 24 hours"

  # Generate automated report
  %(prog)s report

  # Proactive monitoring (runs continuously)
  %(prog)s proactive --interval 15

  # Test system connectivity
  %(prog)s test

  # Show configuration
  %(prog)s config
        """
    )

    parser.add_argument(
        'command',
        choices=['interactive', 'mission', 'report', 'config', 'test', 'proactive'],
        help='Command to execute'
    )

    parser.add_argument(
        'objective',
        nargs='?',
        help='Objective for mission command'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Show detailed reasoning and execution steps'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=15,
        help='Check interval in minutes for proactive monitoring (default: 15)'
    )

    parser.add_argument(
        '--no-slack',
        action='store_true',
        help='Disable Slack notifications for this run'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create CLI instance
    cli = AgentCLI()

    # Route to appropriate command
    try:
        if args.command == 'interactive':
            return cli.cmd_interactive()

        elif args.command == 'mission':
            if not args.objective:
                print("Error: mission command requires an objective")
                print("Usage: cli.py mission 'Your objective here'")
                return 1
            return cli.cmd_mission(args.objective, verbose=args.verbose)

        elif args.command == 'report':
            return cli.cmd_report()

        elif args.command == 'proactive':
            return cli.cmd_proactive(interval=args.interval)

        elif args.command == 'config':
            return cli.cmd_config()

        elif args.command == 'test':
            return cli.cmd_test()

        else:
            parser.print_help()
            return 1

    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        return 130  # Standard exit code for Ctrl+C


if __name__ == "__main__":
    sys.exit(main())
