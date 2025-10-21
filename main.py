import os
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from src.todoist import get_tasks, post_task, update_task
from src.models import Task, TaskUpdate

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
BASE_URL = "https://api.todoist.com/api/v1/"

app = typer.Typer()
console = Console()


@app.command()
def list():
    """
    List all tasks.
    """
    try:
        tasks = get_tasks(API_TOKEN, BASE_URL)
        table = Table(title="Todoist Tasks")
        table.add_column("ID", style="cyan")
        table.add_column("Content", style="magenta")
        table.add_column("Priority", style="green")
        table.add_column("Due Date", style="yellow")

        for task in tasks:
            due_date = task.due.string if task.due else "No due date"
            table.add_row(str(task.id), task.content, str(task.priority), due_date)

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
        console.print(f"[bold green]Task '{new_task.content}' added successfully![/bold green]")
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
            console.print("[bold yellow]No fields to update.[/bold yellow]")
            return

        task = TaskUpdate(**task_data)
        updated_task = update_task(API_TOKEN, BASE_URL, task_id, task)
        console.print(f"[bold green]Task '{updated_task.content}' updated successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")



@app.command()
def tui():
    """
    Launch the Textual TUI.
    """
    from tui import TodoistApp
    app = TodoistApp()
    app.run()


if __name__ == "__main__":
    app()