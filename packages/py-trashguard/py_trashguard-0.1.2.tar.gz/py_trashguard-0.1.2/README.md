# py-trashguard

A safe, user-friendly alternative to `os.remove()` that moves files to a `.trash/` folder instead of deleting them permanently. Use it as a Python API or a CLI tool to protect your files from accidental deletion.

## Features
- **Soft-delete files:** Move files to a `.trash/` directory instead of permanent removal
- **Restore files:** Bring back files from the trash easily
- **List trashed files:** See what’s in your trash
- **No dependencies:** 100% Python standard library

## Installation

Install from PyPI (after publishing):
```bash
pip install py-trashguard
```

Or install from source:
```bash
pip install .
```

## Usage

### Python API Example
```python
from pytrashguard import trash, restore, list_trash

# Move a file to trash
t = trash("myfile.txt")
print(f"Trashed: {t}")

# List trashed files
print("In trash:", list_trash())

# Restore a file from trash
r = restore("myfile.txt")
print(f"Restored: {r}")
```

### Command Line Interface Example
Move a file to trash:
```bash
py-trashguard --trash myfile.txt
```

List trashed files:
```bash
py-trashguard --list
```

Restore a file from trash:
```bash
py-trashguard --restore myfile.txt
```

## Project Structure
- `pytrashguard/core.py`: Core logic
- `pytrashguard/cli.py`: CLI entry point
- `pytrashguard/__init__.py`: API exposure
- `pyproject.toml`: Packaging
- `README.md`: Documentation 