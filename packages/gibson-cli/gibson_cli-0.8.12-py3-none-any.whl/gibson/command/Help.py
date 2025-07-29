from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text

from gibson.command.BaseCommand import BaseCommand


class Help(BaseCommand):
    def execute(self):
        dev_mode_text = []

        if self.configuration.project is not None:
            dev_mode = "on" if self.configuration.project.dev.active is True else "off"
            dev_color = (
                "green" if self.configuration.project.dev.active is True else "red"
            )
            dev_mode_text = [
                "\n\ndev mode is turned ",
                (dev_mode, f"bold {dev_color}"),
            ]

        subcommands = {
            "auth": {
                "description": "authenticate with the gibson cli",
                "subcommands": ["login", "logout"],
            },
            "build": {
                "description": "create the entities in the datastore",
                "subcommands": ["datastore"],
            },
            "code": {
                "description": "pair program with gibson",
                "subcommands": ["api", "base", "entity", "models", "schemas", "tests"],
            },
            "conf": {
                "description": "set a configuration variable",
                "subcommands": None,
            },
            "count": {
                "description": "show the number of entities stored",
                "subcommands": ["last", "stored"],
            },
            "deploy": {
                "description": "deploy the project database(s) with the current schema",
                "subcommands": None,
            },
            "dev": {
                "description": Text.assemble(
                    "gibson will automatically write code for you",
                    *dev_mode_text,
                ),
                "subcommands": ["on", "off"],
            },
            "help": {"description": "for help", "subcommands": None},
            "import": {
                "description": "import entities from a datasource",
                "subcommands": ["api", "mysql", "pg_dump", "openapi"],
            },
            "list": {
                "description": "see a list of your entities or projects",
                "subcommands": ["entities", "projects"],
            },
            "mcp": {
                "description": "allows tools like Cursor to interact with your gibson project",
                "subcommands": ["run"],
            },
            "modify": {
                "description": "change an entity using natural language",
                "subcommands": None,
            },
            "new": {
                "description": "create something new",
                "subcommands": ["project", "module", "entity"],
            },
            "remove": {
                "description": "remove an entity from the project",
                "subcommands": None,
            },
            "rename": {
                "description": "rename an entity",
                "subcommands": ["entity"],
            },
            "rewrite": {
                "description": "rewrite all code",
                "subcommands": None,
            },
            "show": {
                "description": "display an entity",
                "subcommands": None,
            },
            "studio": {
                "description": "connect to your database and launch the SQL studio",
                "subcommands": None,
            },
            "tree": {
                "description": "illustrate the project layout in a tree view",
                "subcommands": None,
            },
            "q": {
                "description": "chat with gibson",
                "subcommands": None,
            },
        }

        self.configuration.display_project()

        console = Console()

        help = Table(
            title=Text.assemble(
                "usage: ",
                (self.configuration.command, "green bold"),
                (" [command]", "yellow bold"),
                (" [subcommand]", "magenta bold"),
            ),
            header_style="bold",
            box=box.ROUNDED,
            expand=True,
            leading=1,
        )
        help.add_column("command", style="yellow bold", header_style="yellow bold")
        help.add_column("description")
        help.add_column("subcommands", header_style="magenta")

        for subcommand, config in subcommands.items():
            help.add_row(
                subcommand,
                config["description"],
                (
                    Text(" | ").join(
                        Text(x, style="magenta") for x in config["subcommands"]
                    )
                    if config["subcommands"]
                    else ""
                ),
            )

        console.print(help)

        self.conversation.newline()
