from urllib.parse import urlparse

from harlequin.app import Harlequin
from harlequin.plugins import load_adapter_plugins

from gibson.api.ProjectApi import ProjectApi
from gibson.command.BaseCommand import BaseCommand
from gibson.core.Select import Select
from gibson.core.Spinner import DisappearingSpinner


class Studio(BaseCommand):
    def execute(self):
        self.configuration.require_login()
        project_id = self.configuration.require_project_id()

        project = ProjectApi(self.configuration).lookup(project_id)

        choices = [database["environment"] for database in project["databases"]]

        selected = Select(
            title="Select a database",
            options=choices,
        ).prompt()

        if not selected:
            self.conversation.type("No database selected\n")
            exit(1)

        database = next(
            (db for db in project["databases"] if db["environment"] == selected), None
        )

        with DisappearingSpinner(
            start_text=f"Connecting to {database['environment']} database...",
            success_text=f"Connected to {database['environment']} database",
            fail_text=f"Failed to connect to {database['environment']} database",
        ):
            plugins = load_adapter_plugins()
            adapter = plugins[database["datastore_type"]]

            if database["datastore_type"] == "mysql":
                connection = urlparse(database["connection_string"])
                adapter = adapter(
                    conn_str=None,
                    host=connection.hostname,
                    port=connection.port,
                    user=connection.username,
                    password=connection.password,
                    database=connection.path.lstrip("/"),
                )
            else:
                raise ValueError(
                    f"Unsupported database type: {database['datastore_type']}"
                )

            app = Harlequin(adapter=adapter)
            app.run()
