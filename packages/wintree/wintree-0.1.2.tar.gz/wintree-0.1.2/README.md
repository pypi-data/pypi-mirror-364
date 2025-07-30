# 📁🌳 wintree

`wintree` is a Python library that displays the hierarchical structure of a specified directory in a tree format. It can be easily used from the command line, supports visually appealing tree views with emojis, and allows you to specify directories to exclude.

## 🚀 Usage

### 📚️ As a Library

```py
import wintree

wintree.print_tree()
```

```bash
# sample output
📂 root: .
├── 📄 .gitignore
├── 📄 README.md
├── 📄 pyproject.toml
├── 📁 src/
│   ├── 📁 assets/
│   │   ├── 📄 icon.png
│   │   └── 📄 splash_android.png
│   └── 📄 main.py
└── 📁 storage/
    ├── 📁 data/
    └── 📁 temp/
```

With arguments:

```py
from wintree import print_tree

print_tree(root_dir="/path/to/project", use_emoji=True, ignore_dirs=[".git", "__pycache__"])
```

| Argument    | Type      | Description                                                                                         |
| ----------- | --------- | --------------------------------------------------------------------------------------------------- |
| root_dir    | str       | Path to the root directory to start displaying the tree. Default is the current directory "."       |
| use_emoji   | bool      | Whether to use emojis in the tree view. If True, adds icons to folders and files.                   |
| ignore_dirs | List[str] | List of directory names to exclude from the tree (partial match). Example: [".git", "node_modules"] |

### ⚙️ Usage from CLI

```bash
python -m wintree.cli /path/to/project --exclude .git __pycache__
```

#### Options

| Option     | Description                                                         |
| ---------- | ------------------------------------------------------------------- |
| path       | Path to the root directory                                          |
| --no-emoji | Disable emoji display                                               |
| --exclude  | Specify directory names to exclude (partial match, space-separated) |

## 📌 Features

- Emoji-based tree view for better visibility
- Flexible exclusion of target directories
- Supports Windows/macOS/Linux
- Pure Python, no external dependencies

## 🧪 For Developers

This library can also be used as a base for directory visualization tools. Integration with GUI tools or IDE plugins is also possible.

## 📄 License

MIT License

# 🌐 Language

- [English](./README.en.md)
- [日本語](./README.ja.md)
