import sys

import anyio
import typer
from rich import print

from daydream.agent.analysis import AnalysisAgent
from daydream.agent.utils import load_agent
from daydream.cli.agent._app import agent_app
from daydream.cli.options import PROFILE_OPTION


@agent_app.command(
    help="Run an agent with the provided payload and print the analysis. A payload can be passed as an argument or piped to stdin."
)
def run(
    agent_name: str = typer.Argument(..., help="The name of the agent to run"),
    payload: str | None = typer.Argument(
        None,
        help="The alert payload to analyze. Alternatively, you can pipe the payload to stdin.",
    ),
    profile: str = PROFILE_OPTION,
    debug: bool = typer.Option(
        False,
        help="Enable debug mode to print the history of the agent.",
    ),
) -> None:
    """Run an agent with the provided payload and print the analysis."""

    async def _run() -> None:
        # Read data from stdin if it's being piped to us.
        if not sys.stdin.isatty():
            if payload is not None:
                print("[red]Cannot pass a payload argument when piping data to stdin.[/red]")
                raise typer.Exit(code=1)
            data = sys.stdin.read().strip()
        else:
            # Otherwise, use the payload argument.
            data = payload

        if not data:
            print("[red]No payload provided.[/red]")
            print(
                "[bold]Pass an alert payload as an argument or pipe the payload data to stdin.[/bold]"
            )
            raise typer.Exit(code=1)

        # Get the config directory and load the specific agent
        try:
            agent = load_agent(agent_name, profile)
        except FileNotFoundError as ex:
            print(f"[red]Agent {agent_name!r} not found at {str(ex.filename)!r}[/red]")
            print(f"[bold]Use 'daydream agent create {agent_name!r}' to create a new agent.[/bold]")
            raise typer.Exit(code=1) from ex

        # Run the analysis with the specific agent
        try:
            analysis_agent = AnalysisAgent(profile)
            result = await analysis_agent.acall(payload=data, agent=agent)
            if debug:
                print("\n\n===== DEBUG OUTPUT =====\n")
                analysis_agent.inspect_history(n=1000)
                print("\n===== END DEBUG OUTPUT =====\n\n")
            print(result)
        except Exception as ex:
            print(f"[red]Analysis failed:[/red] {ex}")
            raise typer.Exit(code=1) from ex

    anyio.run(_run)
