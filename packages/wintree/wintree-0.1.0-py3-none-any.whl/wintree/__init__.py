import os
from typing import List


def print_tree(root_dir: str = ".", use_emoji: bool = True, ignore_dirs: List[str] = []):
    print(f"{"📂 " if use_emoji else ""}root: {root_dir}")
    __make_tree(root_dir, use_emoji=use_emoji, exclude_dirs=ignore_dirs)

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



if __name__ == "__main__":
    print_tree()