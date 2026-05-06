import os
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from typing import Optional

from src.todoist import close_task, get_tasks, post_task, update_task
from src.models import Task, TaskUpdate
from src.task_filters import filter_tasks, sort_tasks_by_due
from src.theme import MONEY_GAZER

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.todoist.com/api/v1/"

app = typer.Typer()
console = Console()


@app.command()
def list(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Only show tasks with this Todoist label/tag."),
    due_close: Optional[int] = typer.Option(
        None,
        "--due-close",
        help="Only show tasks due within this many days. Overdue tasks are included.",
        min=0,
    ),
    sort_by_date: bool = typer.Option(False, "--sort-by-date", "-s", help="Sort tasks by due date."),
    descending: bool = typer.Option(False, "--descending", help="Sort newest due dates first."),
):
    """
    List tasks, optionally filtered by tag and close due date.
    """
    try:
        tasks = filter_tasks(get_tasks(API_TOKEN, BASE_URL), tag=tag, due_close=due_close)
        if sort_by_date:
            tasks = sort_tasks_by_due(tasks, descending=descending)

        table = Table(
            title="Todoist Tasks",
            title_style=f"bold {MONEY_GAZER['primary']}",
            header_style=f"bold {MONEY_GAZER['text']}",
            border_style=MONEY_GAZER["secondary"],
            row_styles=[MONEY_GAZER["text"], MONEY_GAZER["muted_text"]],
        )
        table.add_column("ID", style=MONEY_GAZER["secondary"])
        table.add_column("Content", style=MONEY_GAZER["text"])
        table.add_column("Priority", style=MONEY_GAZER["success"])
        table.add_column("Due Date", style=MONEY_GAZER["primary"])
        table.add_column("Tags", style=MONEY_GAZER["accent"])

        for task in tasks:
            due_date = task.due.string if task.due else "No due date"
            tags = ", ".join(task.labels) if task.labels else "-"
            table.add_row(str(task.id), task.content, str(task.priority), due_date, tags)

        console.print(table)
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@app.command()
def add(
    content: str = typer.Argument(..., help="The content of the task."),
    description: str = typer.Option("", help="The description of the task."),
    project_id: int = typer.Option(None, help="The ID of the project to add the task to."),
    priority: int = typer.Option(4, help="The priority of the task (1-4)."),
):
    """
    Add a new task.
    """
    try:
        task = Task(content=content, description=description, project_id=project_id, priority=priority)
        new_task = post_task(API_TOKEN, BASE_URL, task)
        console.print(f"[bold {MONEY_GAZER['primary']}]Task '{new_task.content}' added successfully![/bold {MONEY_GAZER['primary']}]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@app.command()
def update(
    task_id: str = typer.Argument(..., help="The ID of the task to update."),
    content: str = typer.Option(None, help="The new content of the task."),
    description: str = typer.Option(None, help="The new description of the task."),
    priority: int = typer.Option(None, help="The new priority of the task (1-4)."),
):
    """
    Update a task.
    """
    try:
        task_data = {}
        if content:
            task_data["content"] = content
        if description:
            task_data["description"] = description
        if priority:
            task_data["priority"] = priority

        if not task_data:
            console.print(f"[bold {MONEY_GAZER['primary']}]No fields to update.[/bold {MONEY_GAZER['primary']}]")
            return

        task = TaskUpdate(**task_data)
        updated_task = update_task(API_TOKEN, BASE_URL, task_id, task)
        console.print(f"[bold {MONEY_GAZER['primary']}]Task '{updated_task.content}' updated successfully![/bold {MONEY_GAZER['primary']}]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")



@app.command()
def complete(
    task_id: str = typer.Argument(..., help="The ID of the task to mark complete."),
):
    """
    Mark a task complete.
    """
    try:
        close_task(API_TOKEN, BASE_URL, task_id)
        console.print(f"[bold {MONEY_GAZER['primary']}]Task {task_id} marked complete.[/bold {MONEY_GAZER['primary']}]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")


@app.command()
def tui(
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Only show tasks with this Todoist label/tag."),
    due_close: Optional[int] = typer.Option(
        None,
        "--due-close",
        help="Only show tasks due within this many days. Overdue tasks are included.",
        min=0,
    ),
    sort_by_date: bool = typer.Option(False, "--sort-by-date", "-s", help="Sort tasks by due date."),
):
    """
    Launch the Textual TUI.
    """
    from tui import TodoistApp
    app = TodoistApp(tag=tag, due_close=due_close, sort_by_date=sort_by_date)
    app.run()


if __name__ == "__main__":
    app()