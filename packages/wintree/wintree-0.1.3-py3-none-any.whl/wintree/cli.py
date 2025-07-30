import argparse
from . import print_tree, list_files

def main():
    parser = argparse.ArgumentParser(description="A tool to display directory trees or file listings")
    parser.add_argument("path", help="Path to the root directory")
    parser.add_argument("--no-emoji", action="store_true", help="Hide emojis")
    parser.add_argument("--exclude", nargs="*", default=[], help="Names of directories to exclude (partial match)")
    parser.add_argument("--no-tree", action="store_true", help="Print file paths only (no tree view)")

    args = parser.parse_args()

    if args.no_tree:
        list_files(args.path, ignore_dirs=args.exclude)
    else:
        print_tree(args.path, use_emoji=not args.no_emoji, ignore_dirs=args.exclude)

if __name__ == "__main__":
    main()