# Tentacle Project Structure

## Overview

Tentacle is a Textual-based TUI (Terminal User Interface) application for viewing and managing git diffs. It provides a split-screen interface for browsing files, viewing diffs, and managing git operations.

## File Structure

```
/project-root
├── tentacle/
│   ├── __init__.py
│   ├── main.py
│   ├── git_diff_viewer.py
│   └── git_status_sidebar.py
├── style.tcss
├── README.md
├── pyproject.toml
└── uv.lock
```

## Roles and Responsibilities

### `tentacle/main.py`
- **Role**: Application entry point
- **Responsibilities**:
  - Handle command-line arguments
  - Initialize and run the main Textual application
  - Provide the executable script entry point

### `tentacle/git_diff_viewer.py`
- **Role**: Main Textual application class
- **Responsibilities**:
  - Create and manage the three-panel UI layout (file tree, diff view, commit history)
  - Handle UI events and user interactions
  - Display file diffs with appropriate styling
  - Manage hunk staging/unstaging/discard operations
  - Populate file tree with git status information
  - Populate commit history panel
  - Handle application bindings (quit, dark mode toggle, commit)

### `tentacle/git_status_sidebar.py`
- **Role**: Git repository interaction and data management
- **Responsibilities**:
  - Interface with GitPython to perform git operations
  - Retrieve file statuses (staged, modified, untracked)
  - Parse git diffs into hunks for display
  - Manage staging, unstaging, and discarding of file changes
  - Retrieve commit history
  - Handle commit operations

### `style.tcss`
- **Role**: CSS styling for the Textual application
- **Responsibilities**:
  - Define colors and styles for the application
  - Style UI components (header, footer, panels, buttons)
  - Define styling for different git status indicators
  - Define styling for diff hunks (added, removed, unchanged lines)

### `pyproject.toml`
- **Role**: Project configuration and metadata
- **Responsibilities**:
  - Define project name, version, and description
  - Specify dependencies (textual, GitPython)
  - Define entry points for the application
  - Configure build system

### `uv.lock`
- **Role**: Dependency lock file
- **Responsibilities**:
  - Pin exact versions of all dependencies
  - Ensure reproducible builds

## Running the Project

The project uses UV for Python environment management and should always be run with:

```bash
uv run python -m tentacle.main
```

Or if installed as a package:

```bash
uv run tentacle [repo_path]
```

This ensures that the application runs with the correct Python version and dependencies as managed by UV.
