import json
from .models import Task, TodoistModel, TaskUpdate
from .exception import TodoistException
import requests
from typing import ( List, NoReturn , Any )


def get_tasks(api_token: str, base_url: str) -> List[TodoistModel] | NoReturn:
    """
    Fetches active tasks from Todoist using the REST API directly (without SDK).
    """

    endpoint = "tasks"
    url = f"{base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        tasks_data = response.json()

        tasks = [TodoistModel(**task) for task in tasks_data]
        return tasks
    except requests.exceptions.RequestException as e:
        raise TodoistException("query failed")
    except json.JSONDecodeError as e:
        raise TodoistException("json decode error")
    except Exception as e:
        raise TodoistException(f"Error: {e} {e.__class__.__name__}")




def get_task_by_id(api_token: str, base_url: str, task_id: str) -> TodoistModel:
    """
    Fetches a single task by its ID from Todoist.
    """
    endpoint = f"tasks/{task_id}"
    url = f"{base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }


    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        task_data = response.json()
        return TodoistModel(**task_data)
    except requests.exceptions.RequestException as e:
        raise e
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON response: {e}")
    except Exception as e:
        raise e


def add_task(api_token: str, base_url: str, task: Task) -> Any | NoReturn:
    """
    Creates a new task in Todoist using the REST API directly (without SDK).
    """
    endpoint = "tasks"
    url = f"{base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    data = task.dict()

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        task_data = response.json()
        return TodoistModel(**task_data)
    except requests.exceptions.RequestException as e:
        raise TodoistException("mutation failed")
    except json.JSONDecodeError as e:
        raise TodoistException(" json decode error")
    except Exception as e:
        raise TodoistException(f"Error: {e} {e.__class__.__name__}")


def update_task(
    api_token: str, base_url: str, task_id: str, task: TaskUpdate
) -> TodoistModel:
    """
    Updates a task in Todoist using the REST API directly (without SDK).
    """
    endpoint = f"tasks/{task_id}"
    url = f"{base_url}{endpoint}"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    data = task.dict(exclude_unset=True)

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
        # The update endpoint returns 204 No Content on success, so we fetch the task again to return it
        if response.status_code == 204:
            return get_task_by_id(api_token, base_url, task_id)
        task_data = response.json()
        return TodoistModel(**task_data)
    except requests.exceptions.RequestException as e:
        raise e
    except json.JSONDecodeError as e:
        raise Exception(f"Error decoding JSON response: {e}")
    except Exception as e:
        raise e
