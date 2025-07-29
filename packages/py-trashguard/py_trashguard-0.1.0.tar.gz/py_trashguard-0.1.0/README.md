# py-trashguard

A safe alternative to `os.remove()` that moves files to a `.trash/` folder instead of deleting them permanently. Usable as both a Python API and a CLI tool.

## Features
- Soft-delete files (move to `.trash/`)
- Restore files from trash
- List trashed files
- No third-party dependencies (stdlib only)

## Installation

```bash
pip install .
```

## Usage

### Python API
```python
from pytrashguard import trash, restore, list_trash

trash("myfile.txt")
print(list_trash())
restore("myfile.txt")
```

### CLI
```bash
py-trashguard --trash myfile.txt
py-trashguard --list
py-trashguard --restore myfile.txt
```

## Project Structure
- `pytrashguard/core.py`: Core logic
- `pytrashguard/cli.py`: CLI entry point
- `pytrashguard/__init__.py`: API exposure
- `pyproject.toml`: Packaging
- `README.md`: Documentation 