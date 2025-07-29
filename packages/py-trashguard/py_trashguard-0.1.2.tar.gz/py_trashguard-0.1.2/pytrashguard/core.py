import os
import shutil
import time
from pathlib import Path

DEFAULT_TRASH_DIR = ".trash"

def ensure_trash_dir(base_path: str) -> Path:
    """
    Ensure the .trash directory exists in the given base path.

    Args:
        base_path (str): The directory in which to create/check the .trash folder.

    Returns:
        Path: The Path object for the .trash directory.
    """
    trash_dir = Path(base_path) / DEFAULT_TRASH_DIR
    trash_dir.mkdir(exist_ok=True)
    return trash_dir

def trash(path: str):
    """
    Move a file to the .trash directory, appending a timestamp to its name.

    Args:
        path (str): The path to the file to be trashed.

    Returns:
        Path: The new path of the trashed file inside the .trash directory.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    src = Path(path)
    if not src.exists():
        raise FileNotFoundError(f"{src} does not exist.")
    trash_dir = ensure_trash_dir(src.parent)
    timestamp = int(time.time())
    dest = trash_dir / f"{src.name}.{timestamp}.trashed"
    shutil.move(str(src), dest)
    return dest

def list_trash(base_dir: str = "."):
    """
    List all files currently in the .trash directory of the given base directory.

    Args:
        base_dir (str, optional): The directory containing the .trash folder. Defaults to current directory.

    Returns:
        list: A list of trashed file names.
    """
    trash_dir = Path(base_dir) / DEFAULT_TRASH_DIR
    if not trash_dir.exists():
        return []
    return [f.name for f in trash_dir.iterdir() if f.is_file()]

def restore(filename: str, base_dir: str = "."):
    """
    Restore the most recently trashed file with the given name from the .trash directory.

    Args:
        filename (str): The original name of the file to restore.
        base_dir (str, optional): The directory containing the .trash folder. Defaults to current directory.

    Returns:
        Path: The path to the restored file.

    Raises:
        FileNotFoundError: If no matching trashed file is found.
    """
    trash_dir = Path(base_dir) / DEFAULT_TRASH_DIR
    matches = list(trash_dir.glob(f"{filename}.*.trashed"))
    if not matches:
        raise FileNotFoundError("No such file in trash.")
    # Restore most recent
    latest = sorted(matches, key=lambda f: f.stat().st_mtime)[-1]
    restored_name = filename
    restored_path = Path(base_dir) / restored_name
    shutil.move(str(latest), restored_path)
    return restored_path 