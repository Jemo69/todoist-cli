# Todoist CLI

A small Typer/Textual Todoist client.

## Examples

```bash
# List all active tasks
uv run python main.py list

# Mark a task complete
uv run python main.py complete <task-id>

# Show tasks with a Todoist label/tag
uv run python main.py list --tag work

# Show tasks due within 3 days, including overdue tasks
uv run python main.py list --due-close 3

# Filter by tag and close due date, then sort by due date
uv run python main.py list --tag work --due-close 3 --sort-by-date

# Launch the terminal UI with the same filters
uv run python main.py tui --tag work --due-close 3 --sort-by-date
```

## Theme

The CLI and TUI use the Money Gazer palette. The Textual color scheme lives in `money_gazer.tcss`; shared Rich terminal colors live in `src/theme.py`.

In the TUI:

- `a`: open the add-task form
- `c`: mark the selected task complete
- `r`: refresh tasks
- `s`: toggle date sorting
- `d`: toggle between the Money Gazer light and dark palettes
