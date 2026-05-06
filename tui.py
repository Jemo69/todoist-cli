import os
from typing import Optional

from dotenv import load_dotenv
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Label

from src.models import Task
from src.task_filters import filter_tasks, sort_tasks_by_due
from src.todoist import close_task, get_tasks, post_task

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.todoist.com/api/v1/"


class AddTaskScreen(ModalScreen[Optional[dict]]):
    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Add a task", id="add-task-title"),
            Label("Content"),
            Input(placeholder="What needs to be done?", id="task-content"),
            Label("Description"),
            Input(placeholder="Optional notes", id="task-description"),
            Label("Priority"),
            Input(value="4", placeholder="1-4", restrict="[1-4]", max_length=1, id="task-priority"),
            Horizontal(
                Button("Add task", variant="primary", id="add-task-submit"),
                Button("Cancel", id="add-task-cancel"),
                id="add-task-actions",
            ),
            id="add-task-dialog",
        )

    def on_mount(self) -> None:
        self.query_one("#task-content", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "add-task-cancel":
            self.dismiss(None)
        elif event.button.id == "add-task-submit":
            self.submit_task()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "task-priority":
            self.submit_task()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def submit_task(self) -> None:
        content = self.query_one("#task-content", Input).value.strip()
        description = self.query_one("#task-description", Input).value.strip()
        priority_value = self.query_one("#task-priority", Input).value.strip() or "4"

        if not content:
            self.notify("Task content is required", severity="warning")
            self.query_one("#task-content", Input).focus()
            return

        try:
            priority = int(priority_value)
        except ValueError:
            priority = 4

        if priority not in {1, 2, 3, 4}:
            self.notify("Priority must be between 1 and 4", severity="warning")
            self.query_one("#task-priority", Input).focus()
            return

        self.dismiss({"content": content, "description": description, "priority": priority})


class TodoistApp(App):
    CSS_PATH = "money_gazer.tcss"
    TITLE = "Todoist CLI"
    SUB_TITLE = "Money Gazer"

    BINDINGS = [
        ("a", "add_task", "Add task"),
        ("c", "complete_selected", "Complete selected task"),
        ("r", "refresh_tasks", "Refresh tasks"),
        ("s", "toggle_sort_by_date", "Toggle date sort"),
        ("d", "toggle_dark", "Toggle dark mode"),
    ]

    def __init__(
        self,
        tag: Optional[str] = None,
        due_close: Optional[int] = None,
        sort_by_date: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.tag = tag
        self.due_close = due_close
        self.sort_by_date = sort_by_date

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "Content", "Priority", "Due Date", "Tags")
        self.load_tasks()

    def load_tasks(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        try:
            tasks = filter_tasks(get_tasks(API_TOKEN, BASE_URL), tag=self.tag, due_close=self.due_close)
            if self.sort_by_date:
                tasks = sort_tasks_by_due(tasks)

            for task in tasks:
                due_date = task.due.string if task.due else "No due date"
                tags = ", ".join(task.labels) if task.labels else "-"
                table.add_row(task.id, task.content, str(task.priority), due_date, tags, key=task.id)
        except Exception as e:
            self.log(f"Error getting tasks: {e}")
            self.notify(f"Error getting tasks: {e}", severity="error")

    def action_add_task(self) -> None:
        self.push_screen(AddTaskScreen(), self.add_task)

    def add_task(self, task_data: Optional[dict]) -> None:
        if not task_data:
            return

        try:
            task = Task(
                content=task_data["content"],
                description=task_data["description"],
                project_id=None,
                priority=task_data["priority"],
            )
            new_task = post_task(API_TOKEN, BASE_URL, task)
            self.notify(f"Task '{new_task.content}' added")
            self.load_tasks()
        except Exception as e:
            self.log(f"Error adding task: {e}")
            self.notify(f"Error adding task: {e}", severity="error")

    def action_complete_selected(self) -> None:
        table = self.query_one(DataTable)
        if table.row_count == 0 or not table.is_valid_row_index(table.cursor_row):
            self.notify("No task selected", severity="warning")
            return

        task_id = str(table.get_row_at(table.cursor_row)[0])
        try:
            close_task(API_TOKEN, BASE_URL, task_id)
            self.notify(f"Task {task_id} marked complete")
            self.load_tasks()
        except Exception as e:
            self.log(f"Error completing task: {e}")
            self.notify(f"Error completing task: {e}", severity="error")

    def action_refresh_tasks(self) -> None:
        self.load_tasks()
        self.notify("Tasks refreshed")

    def action_toggle_sort_by_date(self) -> None:
        self.sort_by_date = not self.sort_by_date
        self.load_tasks()
        self.notify(f"Sort by date {'on' if self.sort_by_date else 'off'}")

    def action_toggle_dark(self) -> None:
        self.dark = not self.dark


if __name__ == "__main__":
    app = TodoistApp()
    app.run()
