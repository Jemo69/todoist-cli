
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer
from src.todoist import get_tasks
from src.models import TodoistModel
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.todoist.com/api/v1/"

class TodoistApp(App):
    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Content", "Priority", "Due Date")
        try:
            tasks = get_tasks(API_TOKEN, BASE_URL)
            for task in tasks:
                due_date = task.due.string if task.due else "No due date"
                table.add_row(task.id, task.content, str(task.priority), due_date)
        except Exception as e:
            self.log(f"Error getting tasks: {e}")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark

if __name__ == "__main__":
    app = TodoistApp()
    app.run()
