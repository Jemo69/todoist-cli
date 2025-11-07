from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Button, Input, Label
from textual.containers import Vertical
from textual.screen import Screen
from textual import on 
from src.todoist import get_tasks, add_task  
from src.models import TodoistModel, Task
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.todoist.com/api/v1/"


class ViewTasksScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.update_tasks()

    def update_tasks(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        table.add_columns("ID", "Content","Description", "Priority", "Due Date")
        try:
            if API_TOKEN is None:
                return
            tasks = get_tasks(API_TOKEN, BASE_URL)
            for task in tasks:
                due_date = task.due.string if task.due else "No due date"
                table.add_row(task.id, task.content,task.description, str(task.priority), due_date)
        except Exception as e:
            self.app.log(f"Error getting tasks: {e}")


class AddTaskScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Label("Task Content:", id="content_label"),
            Input(placeholder="Task description", id="content_input"),
            Label(
                "Due Date (e.g., 'today', 'tomorrow', '2025-12-31'):",
                id="due_date_label",
            ),
            Input(placeholder="description", id="description_input"),
            Label("Priority (1-4, 4 is highest):", id="priority_label"),
            Input(placeholder="Priority", id="priority_input"),
            Button("Add Task", id="add_task_button", variant="primary"),
            Button("Cancel", id="cancel_button"),
        )
        yield Footer()

    @on(Button.Pressed )
    async def add_task(self, event: Button.Pressed) -> None:
        if event.button.id == "add_task_button":
            content = self.query_one("#content_input", Input).value
            due_date = self.query_one("#description_input", Input).value
            priority = self.query_one("#priority_input", Input).value

            if not content:
                self.app.bell()
                self.app.log("Task content cannot be empty.")
                return

            try:
                priority_int = int(priority) if priority else 1
                new_task_obj = Task(
                    content=content, description=due_date, priority=priority_int
                )
                assert API_TOKEN is not None

                new_task = add_task(API_TOKEN, BASE_URL, new_task_obj)
                assert not isinstance(new_task, str)
                self.app.log(f"Task added: {new_task.content}")
                self.app.switch_screen("view_tasks")
                self.app.query_one(ViewTasksScreen).update_tasks()
            except Exception as e:
                self.app.log(f"Error adding task: {e}")
        elif event.button.id == "cancel_button":
            self.app.switch_screen("view_tasks")


class TodoistApp(App):
    BINDINGS = [
        ("a", "add_task_screen", "Add Task"),
        ("v", "view_tasks_screen", "View Tasks"),
    ]

    SCREENS = {
        "view_tasks": ViewTasksScreen,
        "add_task": AddTaskScreen,
    }

    def on_mount(self) -> None:
        self.push_screen("view_tasks")

    def action_add_task_screen(self) -> None:
        self.push_screen("add_task")

    def action_view_tasks_screen(self) -> None:
        self.push_screen("view_tasks")


if __name__ == "__main__":
    app = TodoistApp()
    app.run()
