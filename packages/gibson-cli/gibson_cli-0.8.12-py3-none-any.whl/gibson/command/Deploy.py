from rich.prompt import Confirm

from gibson.api.ProjectApi import ProjectApi
from gibson.command.BaseCommand import BaseCommand
from gibson.core.Select import MultiSelect
from gibson.core.Spinner import Spinner


class Deploy(BaseCommand):
    def execute(self):
        self.configuration.require_login()
        project_id = self.configuration.require_project_id()
        project = ProjectApi(self.configuration).lookup(project_id)
        databases = [database["environment"] for database in project["databases"]]

        selected = MultiSelect(
            title="Select the database(s) to deploy",
            options=databases,
        ).prompt()

        if not selected:
            self.conversation.type("No database selected\n")
            exit(1)

        for database in selected:
            diff = ProjectApi(self.configuration).diff(project_id)
            if diff:
                self.conversation.type(f"\nDiff for {database} database:\n\n")
                self.conversation.type(diff)
                self.conversation.newline()

                if Confirm.ask(
                    f"After reviewing the diff, are you sure you want to deploy the {database} database?"
                ):
                    self.conversation.newline()
                    with Spinner(
                        start_text=f"Deploying {database} database...",
                        success_text=f"Deployed {database} database",
                        fail_text=f"Deployment failed for {database} database",
                    ):
                        ProjectApi(self.configuration).deploy(
                            project_id, databases=[database]
                        )

                else:
                    self.conversation.type(
                        f"\nSkipping deployment for {database} database\n",
                    )
            else:
                self.conversation.type(
                    f"\nNo changes to deploy for {database} database\n",
                )
