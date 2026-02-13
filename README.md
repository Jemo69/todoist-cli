# Todoist CLI

A command-line tool to manage your Todoist tasks.

## Installation

```bash
pip install todoist-cli
```

Or install from source:

```bash
uv pip install -e .
```

## Usage

### Setup

Run the setup command to configure your API token:

```bash
todoist setup
```

### Commands

- **List tasks**: `todoist list`
- **Add task**: `todoist add "My new task"`
- **Update task**: `todoist update <task-id> --content "Updated content"`
- **Launch TUI**: `todoist tui`

### Options

- `--help` - Show help message

## Features

- List all your Todoist tasks
- Add new tasks with priority
- Update existing tasks
- Textual-based TUI for interactive task management
