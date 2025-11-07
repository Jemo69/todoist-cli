use uv when you  want to run python code 
this some command you need to know

  auth     Manage authentication
  run      Run a command or script
  init     Create a new project
  add      Add dependencies to the project
  remove   Remove dependencies from the project
  version  Read or update the project's version
  sync     Update the project's environment
  lock     Update the project's lockfile
  export   Export the project's lockfile to an alternate format
  tree     Display the project's dependency tree
  format   Format Python code in the project
  tool     Run and install commands provided by Python packages
  python   Manage Python versions and installations
  pip      Manage Python packages with a pip-compatible interface
  venv     Create a virtual environment
  build    Build Python packages into source distributions and wheels
  publish  Upload distributions to an index
  cache    Manage uv's cache
  self     Manage the uv executable
  help     Display documentation for a command

Cache options:
  -n, --no-cache               Avoid reading from or writing to the cache, instead using a temporary directory for the duration of the operation [env: UV_NO_CACHE=]
      --cache-dir <CACHE_DIR>  Path to the cache directory [env: UV_CACHE_DIR=]

Python options:
      --managed-python       Require use of uv-managed Python versions [env: UV_MANAGED_PYTHON=]
      --no-managed-python    Disable use of uv-managed Python versions [env: UV_NO_MANAGED_PYTHON=]
      --no-python-downloads  Disable automatic downloads of Python. [env: "UV_PYTHON_DOWNLOADS=never"]

Global options:
  -q, --quiet...                                   Use quiet output
  -v, --verbose...                                 Use verbose output
      --color <COLOR_CHOICE>                       Control the use of color in output [possible values: auto, always, never]
      --native-tls                                 Whether to load TLS certificates from the platform's native certificate store [env: UV_NATIVE_TLS=]
      --offline                                    Disable network access [env: UV_OFFLINE=]
      --allow-insecure-host <ALLOW_INSECURE_HOST>  Allow insecure connections to a host [env: UV_INSECURE_HOST=]
      --no-progress                                Hide all progress outputs [env: UV_NO_PROGRESS=]
      --directory <DIRECTORY>                      Change to the given directory prior to running the command [env: UV_WORKING_DIRECTORY=]
      --project <PROJECT>                          Run the command within the given project directory [env: UV_PROJECT=]
      --config-file <CONFIG_FILE>                  The path to a `uv.toml` file to use for configuration [env: UV_CONFIG_FILE=]
      --no-config                                  Avoid discovering configuration files (`pyproject.toml`, `uv.toml`) [env: UV_NO_CONFIG=]
  -h, --help                                       Display the concise help for this command
  -V, --version                                    Display the uv version
Here is the official documentation for the Textual **Worker** system, which replaces the removed `run_in_thread` function.

The key concepts for running background tasks are the **`@work` decorator** and the **`run_worker`** method.

-----

## 👨‍🏭 Textual Workers Documentation

Textual's **Worker** system handles running tasks in the background, preventing your TUI from freezing, and integrating neatly with the event loop.

### 1\. The `@work` Decorator (Recommended)

This is the easiest and most common way to run a method in the background. You apply it directly to a method within an `App`, `Screen`, or `Widget`.

| Syntax | Description |
| :--- | :--- |
| `@work` | Schedules the decorated method to run in the background as an **asynchronous task** (non-blocking). |
| `@work(thread=True)` | Schedules the decorated method to run in a **separate thread** (ideal for **blocking** I/O or CPU-heavy functions). This is the direct replacement for the functionality of the old `run_in_thread`. |

#### **Usage Example**

```python
from textual.app import App, ComposeResult
from textual.app import work # Import the decorator

class MyWidget(Static):
    # This method will run in a separate thread (thread=True) 
    # and not block the TUI.
    @work(thread=True)
    def my_blocking_task(self, filename: str):
        # Time-consuming file I/O or network request
        data = self.load_file(filename) 
        
        # To communicate back to the UI, you must post a message 
        # or use call_from_thread.
        self.post_message(TaskComplete(data)) 

    # Handler for a button press to start the task
    def on_button_pressed(self):
        self.my_blocking_task("config.json") 
        # Calling this decorated method starts the worker immediately.
```

### 2\. The `run_worker` Method

You can explicitly create and start a worker using the `run_worker` method available on `App`, `Screen`, and `Widget`. This gives you a `Worker` object for more control.

#### **Method Signature**

```python
# From a Widget/Screen/App instance (e.g., self)
self.run_worker(
    work: WorkType,
    *,
    name: str = "",
    group: str = "default",
    exit_on_error: bool = True,
    exclusive: bool = False,
    description: str = "",
    thread: bool = False, # Set this to True for thread workers
) -> Worker
```

#### **Usage Example**

```python
# To run a separate function (not a method) in a thread:
def fetch_data():
    # Blocking I/O...
    return "The result"

class MyComponent(Static):
    def fetch_button_pressed(self):
        # This will run fetch_data in a new thread
        worker = self.run_worker(fetch_data, thread=True) 
        
        # Now you have a Worker object you can interact with:
        # worker.cancel() 
        # worker.wait() (must be awaited from an async function)
```

### 3\. Key `Worker` Parameters

| Parameter | Type | Description |
| :--- | :--- | :--- |
| `thread` | `bool` | Set to `True` to run the task in a **separate thread** (`threading.Thread`). Use this for blocking synchronous code. |
| `exclusive` | `bool` | If `True`, any existing workers in the same `group` will be cancelled before this new one starts. Useful for quickly replacing an outdated search or request. |
| `exit_on_error` | `bool` | If `True`, the entire app will exit if the worker raises an uncaught exception. Set to `False` to prevent this. |

### 4\. Communicating Back to the UI

You **must not** directly update the Textual UI from a **thread worker** (i.e., when `thread=True`).

  * **For simple UI updates:** Use the `self.call_from_thread()` method.
    ```python
    # Inside the thread worker method:
    self.call_from_thread(self.query_one(Label).update, "Task complete!")
    ```
  * **For complex results:** Post a custom message. This is the preferred pattern.
    ```python
    # Inside the thread worker method:
    self.post_message(MyCustomMessage(result_data)) 

    # In the App/Widget:
    def on_my_custom_message(self, message: MyCustomMessage):
        self.query_one(Input).value = message.data
    ```

-----

The functionality of `run_in_thread` is now covered by either `@work(thread=True)` or `self.run_worker(..., thread=True)`.

Would you like me to show you an example of how to replace the old `from textual.worker import run_in_thread` statement in your specific `tui.py` file with the modern `@work` decorator?
