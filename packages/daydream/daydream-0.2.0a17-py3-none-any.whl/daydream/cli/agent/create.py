import os
from pathlib import Path

import anyio
import typer
from rich import print

from daydream.agent.utils import get_agent_template
from daydream.cli.agent._app import agent_app
from daydream.cli.options import PROFILE_OPTION
from daydream.config.utils import get_config_dir
from daydream.utils import edit_file


@agent_app.command()
def create(
    agent_name: str = typer.Argument(..., help="The name of the agent to create"),
    profile: str = PROFILE_OPTION,
    overwrite: bool = typer.Option(False, help="Overwrite the agent file if it already exists"),
    template: str = typer.Option("blank", help="The template to use to create the agent file"),
    editor: str = typer.Option(
        os.environ.get("EDITOR"), help="The editor to use to open the agent file"
    ),
    no_edit: bool = typer.Option(False, help="Do not open the agent file in your editor"),
) -> None:
    """Create a new agent configuration file and open it in your editor."""

    async def _create() -> None:
        # Create the default YAML content
        try:
            agent_template = get_agent_template(template)
        except FileNotFoundError as ex:
            print(
                f"Template '{template}' not found at {Path(__file__).parent / 'templates' / f'{template}.yaml'}"
            )
            raise typer.Abort() from ex

        # Get the config directory for the profile
        config_dir = get_config_dir(profile, create=True)

        # Create the agents directory if it doesn't exist
        agents_dir = config_dir / "agents"
        agents_dir.mkdir(exist_ok=True)

        # Create the agent file path
        agent_file = agents_dir / f"{agent_name}.yaml"

        # Check if the agent file already exists
        if agent_file.exists():
            if overwrite:
                print(f"Overwriting agent '{agent_name}' at {agent_file}")
            else:
                print(f"Agent '{agent_name}' already exists at {agent_file}")
                if not typer.confirm("Do you want to overwrite it?"):
                    raise typer.Abort()

        # Write the YAML content to the file
        agent_file.write_text(agent_template, encoding="utf-8")

        print(f"Created agent configuration at {agent_file}")

        # Open the file in the user's editor
        if editor and not no_edit:
            try:
                await edit_file(agent_file, editor)
            except ValueError as ex:
                print(
                    "[red]No editor specified. Set the $EDITOR environment variable or use --editor option.[/red]"
                )
                print(f"[blue]Please manually open {str(agent_file)!r} in your editor.[/blue]")
                raise typer.Exit() from ex

    anyio.run(_create)
