from datetime import date, timedelta
from typing import Iterable, Optional

from .models import TodoistModel


def due_date_value(task: TodoistModel) -> Optional[date]:
    """Return the task due date as a date object, or None when absent/invalid."""
    if not task.due or not task.due.date:
        return None

    try:
        return date.fromisoformat(task.due.date[:10])
    except ValueError:
        return None


def normalize_tag(tag: Optional[str]) -> Optional[str]:
    """Normalize user supplied Todoist label/tag names."""
    if tag is None:
        return None
    tag = tag.strip()
    if tag.startswith("#"):
        tag = tag[1:]
    return tag or None


def filter_tasks(
    tasks: Iterable[TodoistModel],
    tag: Optional[str] = None,
    due_close: Optional[int] = None,
) -> list[TodoistModel]:
    """Filter tasks by Todoist label and/or due date closeness."""
    normalized_tag = normalize_tag(tag)
    today = date.today()
    close_until = today + timedelta(days=due_close) if due_close is not None else None

    filtered: list[TodoistModel] = []
    for task in tasks:
        if normalized_tag and normalized_tag not in task.labels:
            continue

        if close_until is not None:
            due_date = due_date_value(task)
            if due_date is None or due_date > close_until:
                continue

        filtered.append(task)

    return filtered


def sort_tasks_by_due(tasks: Iterable[TodoistModel], descending: bool = False) -> list[TodoistModel]:
    """Sort tasks by due date. Tasks without due dates are always placed last."""
    dated_tasks: list[TodoistModel] = []
    undated_tasks: list[TodoistModel] = []

    for task in tasks:
        if due_date_value(task) is None:
            undated_tasks.append(task)
        else:
            dated_tasks.append(task)

    dated_tasks.sort(key=lambda task: due_date_value(task) or date.max, reverse=descending)
    return dated_tasks + undated_tasks
