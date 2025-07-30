import argparse
from . import print_tree

def main():
    parser = argparse.ArgumentParser(description="A tool to display directory trees")
    parser.add_argument("path", help="Path to the root directory")
    parser.add_argument("--no-emoji", action="store_true", help="Hide emojis")
    parser.add_argument("--exclude", nargs="*", default=[], help="Names of directories to exclude (partial match)")

    args = parser.parse_args()
    print_tree(args.path, use_emoji=not args.no_emoji, ignore_dirs=args.exclude)

if __name__ == "__main__":
    main()