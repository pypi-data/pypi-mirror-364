import argparse
from pytrashguard.core import trash, restore, list_trash

def main():
    """
    Command-line interface for py-trashguard.

    Provides the following options:
        --trash <file>: Soft delete a file (move to .trash)
        --restore <name>: Restore a file from .trash
        --list: List files in .trash
    """
    parser = argparse.ArgumentParser(description="TrashGuard: soft delete your files safely.")
    parser.add_argument('--trash', help='Soft delete a file')
    parser.add_argument('--restore', help='Restore a file from trash')
    parser.add_argument('--list', action='store_true', help='List files in trash')

    args = parser.parse_args()

    if args.trash:
        result = trash(args.trash)
        print(f"Moved to trash: {result}")
    elif args.restore:
        result = restore(args.restore)
        print(f"Restored: {result}")
    elif args.list:
        files = list_trash()
        if not files:
            print("Trash is empty.")
        else:
            for f in files:
                print(f)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 