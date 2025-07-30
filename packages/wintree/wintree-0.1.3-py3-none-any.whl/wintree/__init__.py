import os
from typing import List


def print_tree(root_dir: str = ".", use_emoji: bool = True, ignore_dirs: List[str] = []):
    """
    Display the directory structure as a tree.

    Args:
        root_dir (str, optional): Path to the root directory to display. Defaults to "." (current directory).
        use_emoji (bool, optional): If True, display emojis for folders and files. Defaults to True.
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the tree. Defaults to [].

    Example:
        ```
        print_tree(root_dir="/path/to/project", use_emoji=True, ignore_dirs=[".git", "__pycache__"])
        ```
    """
    print(f"{'📂 ' if use_emoji else ''}root: {root_dir}")
    __make_tree(root_dir, use_emoji=use_emoji, exclude_dirs=ignore_dirs)

def list_files(root_dir: str = ".", ignore_dirs: List[str] = []):
    """
    Recursively list all files under the specified directory, excluding specified directories.

    Args:
        root_dir (str, optional): Path to the root directory to search. Defaults to "." (current directory).
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the search. Defaults to [].

    Example:
        ```
        list_files(root_dir="/path/to/project", ignore_dirs=[".git", "__pycache__"])
        ```
    """
    __list_files_recursive(root_dir, ignore_dirs)

def __make_tree(current_dir, prefix="", use_emoji=True, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []

    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return

    entries = [e for e in entries if not any(ex in os.path.join(current_dir, e) for ex in exclude_dirs)]

    for idx, entry in enumerate(entries):
        full_path = os.path.join(current_dir, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        icon_folder = "📁 " if use_emoji else ""
        icon_file = "📄 " if use_emoji else ""

        if os.path.isdir(full_path):
            print(f"{prefix}{connector}{icon_folder}{entry}/")
            extension = "    " if idx == len(entries) - 1 else "│   "
            __make_tree(full_path, prefix + extension, use_emoji, exclude_dirs)
        else:
            print(f"{prefix}{connector}{icon_file}{entry}")

def __list_files_recursive(current_dir, exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = []

    try:
        entries = os.listdir(current_dir)
    except PermissionError:
        return

    for entry in entries:
        full_path = os.path.join(current_dir, entry)

        if any(ex in full_path for ex in exclude_dirs):
            continue

        if os.path.isdir(full_path):
            __list_files_recursive(full_path, exclude_dirs)
        else:
            print(os.path.abspath(full_path))


if __name__ == "__main__":
    print_tree(ignore_dirs=[".git", "__pycache__"])
    print("\n" + "-"*40 + "\n")
    list_files(ignore_dirs=[".git", "__pycache__"])