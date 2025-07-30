import os
from typing import List


def tree(root_dir: str = ".", use_emoji: bool = True, ignore_dirs: List[str] = [], filter_exts: List[str] = []):
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
    root_str = f"{'📂 ' if use_emoji else ''}root: {root_dir}"
    tree = __make_tree(root_dir, use_emoji=use_emoji, exclude_dirs=ignore_dirs, filter_exts=filter_exts)
    return f"{root_str}\n{tree}" if tree else f"{root_str}\n(No files or directories found)"

def list_files(root_dir: str = ".", ignore_dirs: List[str] = [], filter_exts: List[str] = []):
    """
    Recursively list all files under the specified directory, excluding specified directories.

    Args:
        root_dir (str, optional): Path to the root directory to search. Defaults to "." (current directory).
        ignore_dirs (List[str], optional): List of directory names (partial match) to exclude from the search. Defaults to [].

    Example:
        ```
        print(list_files(root_dir="/path/to/project", ignore_dirs=[".git", "__pycache__"]))
        ```
    """
    return __list_files_recursive(root_dir, ignore_dirs, filter_exts)

def __make_tree(current_dir, prefix="", use_emoji=True, exclude_dirs=None, filter_exts=None):
    output_str = ""

    if exclude_dirs is None:
        exclude_dirs = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = sorted(os.listdir(current_dir))
    except PermissionError:
        return ""

    entries = [e for e in entries if not any(ex in os.path.join(current_dir, e) for ex in exclude_dirs)]

    for idx, entry in enumerate(entries):
        full_path = os.path.join(current_dir, entry)
        connector = "└── " if idx == len(entries) - 1 else "├── "
        icon_folder = "📁 " if use_emoji else ""
        icon_file = "📄 " if use_emoji else ""

        if os.path.isdir(full_path):
            output_str += f"{prefix}{connector}{icon_folder}{entry}/\n"
            extension = "    " if idx == len(entries) - 1 else "│   "
            output_str += __make_tree(full_path, prefix + extension, use_emoji, exclude_dirs, filter_exts)
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue
            output_str += f"{prefix}{connector}{icon_file}{entry}\n"

    return output_str

def __list_files_recursive(current_dir, exclude_dirs=None, filter_exts=None):
    output_str = ""

    if exclude_dirs is None:
        exclude_dirs = []
    if filter_exts is None:
        filter_exts = []

    try:
        entries = os.listdir(current_dir)
    except PermissionError:
        return

    for entry in entries:
        full_path = os.path.join(current_dir, entry)

        if any(ex in full_path for ex in exclude_dirs):
            continue

        if os.path.isdir(full_path):
            child = __list_files_recursive(full_path, exclude_dirs, filter_exts)
            output_str += child if child else ""
        else:
            _, ext = os.path.splitext(entry)
            if filter_exts and ext.lower() not in [e.lower() for e in filter_exts]:
                continue

            output_str += (os.path.abspath(full_path) + "\n")

    return output_str


if __name__ == "__main__":
    print(tree(ignore_dirs=[".git", "__pycache__"]))
    print("\n" + "-"*40 + "\n")
    print(list_files(ignore_dirs=[".git", "__pycache__"]))