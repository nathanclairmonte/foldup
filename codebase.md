# PROJECT TREE

foldup
├─ .gitignore
├─ .python-version
├─ .ruff_cache
├─ pyproject.toml
├─ README.md
├─ src
│   ├─ __init__.py
│   ├─ cli.py
│   ├─ core.py
│   ├─ defaults.py
│   └─ utils.py
├─ Taskfile.yml
└─ tests

# .gitignore

```plaintext
# Python-generated files
__pycache__/
*.py[oc]
build/
dist/
wheels/
*.egg-info

# Virtual environments
.venv

# VSCode
.vscode/

# Ruff
.ruff_cache/

# Fold
.foldignore
```

# .python-version

```plaintext
3.12

```

# pyproject.toml

```toml
[project]
name = "foldup"
version = "0.1.0"
description = "Fold your codebase into a single Markdown file for passing to an LLM."
readme = "README.md"
requires-python = ">=3.9"
dependencies = [
    "click>=8.1.7",
    "pathspec>=0.12.1",
    "pyyaml>=6.0.2",
    "tiktoken>=0.8.0",
]

[dependency-groups]
dev = [
    "ruff>=0.8.2",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project.scripts]
foldup = "src.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src"]

```

# README.md

```markdown
# foldup

A command-line tool that "folds" your codebase into a single Markdown file that can easily be fed into an LLM.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/nathanclairmonte/foldup.git
cd foldup
```

2. Install as a CLI tool:
```bash
pip install .
```

Now you ~~can~~ _should be able to_ run `foldup` from anywhere in your system! Lmk if anything doesn't work though.

## Usage

```bash
# Process current directory
foldup
```

### Run with Options

```bash
# Process specific directory
foldup /path/to/project

# Custom output filename (default: codebase.md)
foldup -o output.md

# Display list of processed & skipped files
foldup --show-files

# Display estimated token count (takes a few extra ms)
foldup --estimate-tokens

# Use custom config file (defaults to foldup.yaml in project root)
foldup -c custom-config.yaml

# Set maximum input file size (in MB)
foldup --max-size 2.5
```

## Configuration

You can configure foldup using two methods:

1. **.foldignore File**:
Create a `.foldignore` file in your project root:
```
# Example .foldignore
*.log
temp/
*.pyc
.DS_Store
```

2. **Config File (foldup.yaml)**:
```yaml
# Default config
exclude:
  # common things to ignore
  - __pycache__
  - node_modules
  - .git
  - venv
  - .venv
  - .env
  - .env.*
  - .idea
  - .vscode
  - dist
  - build
  - .next
  - coverage
  # foldup-related
  - codebase.md
  - .foldignore
  - foldup.yaml
max_file_size_mb: 1.0
include_binary_files: false
show_processed_files: false
estimate_tokens: false
```

## Output Format

The generated markdown file includes:
1. Project tree visualization
2. Filepath and contents of each file

Example output:
````markdown
# PROJECT TREE

myproject
├─ .gitignore
├─ README.md
└─ src
   ├─ main.py
   └─ utils.py

# .gitignore

```
node_modules
*.log
```

# README.md

```md
# My Project
Lorem ipsum
```

# src/main.py

```python
def main():
    print("Hello, World!")
```

# src/utils.py

```python
def multiply(a, b):
    return a * b
```
````

## Estimated Token Count

The estimated token count can be optionally displayed by passing the `--estimate-tokens` flag. Foldup uses the [tiktoken](https://github.com/openai/tiktoken) library to estimate token count. Remember that this is just an estimate, the actual token count may vary (but probably not by an insane amount).


> [!NOTE] 
> Tiktoken uses the GPT-4 tokenizer. For ChatGPT, it should be relatively close. For Claude, it could be off by ±20%.


## Development

1. Clone the repository:
```bash
git clone https://github.com/nathanclairmonte/foldup.git
cd foldup
```

2. Install dependencies:
```bash
uv sync
```

3. Make any changes you want to the code!

4. Run the CLI tool locally:
```bash
uv run python -m src.cli
```

---

## TODO

- [x] Add Taskfile for linting, testing, building, etc.
- [x] Add support for a `.foldignore` file
- [x] Facilitate estimating the number of tokens in the output file
- [x] Rename to `foldup` (I think?). Sounds nicer lol and easier to type `foldup` than `fold-cli` like i have it rn
- [x] Update README with installation and usage instructions
- [ ] Add an `--only-tree` flag to only generate just the project tree and not the file contents
- [ ] Faciliate glob patterns for excluding files in config or `.foldignore`
- [ ] Add `--version` flag
- [ ] Sort list of output files by size (number of lines? number of chars or tokens?)
- [ ] Exclude image files as well, or any other non-text files
- [ ] Tests
- [ ] Add license
- [ ] Package for release on PyPI: https://packaging.python.org/en/latest/tutorials/packaging-projects/
- [ ] Add badges to README
- [ ] Add GitHub Actions for linting, testing, building, and releasing

```

# src\__init__.py

```python

```

# src\cli.py

```python
from pathlib import Path

import click

from src.core import generate_markdown
from src.utils import get_estimated_token_count, read_config


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "-o",
    "--output",
    type=click.Path(),
    default="codebase.md",
    help="Output file path (default: codebase.md)",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=False),
    default="foldup.yaml",
    help="Config file path (default: foldup.yaml)",
)
@click.option(
    "--max-size",
    type=float,
    default=1.0,
    help="Maximum file size in MB to process (default: 1.0)",
)
@click.option(
    "-sf",
    "--show-files",
    is_flag=True,
    default=False,
    help="Include list of processed files in output (default: False)",
)
@click.option(
    "-t",
    "--estimate-tokens",
    is_flag=True,
    default=False,
    help="Estimate tokens in output (default: False)",
)
def main(
    path: str,
    output: str,
    config: str,
    max_size: float,
    show_files: bool,
    estimate_tokens: bool,
) -> None:
    """
    Fold a codebase into a single markdown file for LLM consumption.

    Args:
        path: Directory to process (defaults to current directory)
    """
    try:
        # convert paths to Path objects
        root_path = Path(path).resolve()
        output_path = Path(output)
        config_path = Path(config)

        # read configuration
        config_data = read_config(config_path, root_path)

        # override config values with command line options
        if max_size != 1.0:
            config_data["max_file_size_mb"] = max_size
        if show_files:
            config_data["show_processed_files"] = True
        if estimate_tokens:
            config_data["estimate_tokens"] = True

        # generate the markdown
        click.echo(f"Processing directory: {root_path}")
        content, stats = generate_markdown(
            root_path,
            config_data["pathspec"],
            config_data["max_file_size_mb"],
        )

        # write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # calculate output file size
        output_size = output_path.stat().st_size / 1024  # size in KB

        # print statistics to terminal
        click.echo("\nProcessing Statistics:")
        click.echo(f"Files processed: {stats['processed_files']}")
        click.echo(f"Files skipped: {stats['skipped_files']}")
        click.echo(f"Total source size processed: {stats['total_size'] / 1024:.1f} KB")
        click.echo(f"Output file size: {output_size:.1f} KB")
        if estimate_tokens or config_data.get("estimate_tokens", False):
            token_count = get_estimated_token_count(content)
            if token_count > 0:
                click.echo(f"Estimated tokens (GPT-4): {token_count:,}")

        if show_files or config_data.get("show_processed_files", False):
            if stats["processed_file_list"]:
                click.echo("\nFiles processed:")
                for file_path in sorted(stats["processed_file_list"]):
                    click.echo(f"{click.style('*', fg='green')} {file_path}")

            if stats["skipped_file_list"]:
                click.echo("\nFiles skipped:")
                for file_path in sorted(stats["skipped_file_list"]):
                    click.echo(f"{click.style('*', fg='red')} {file_path}")

        click.echo(
            f"\nDone! Output written to: {click.style(str(output_path), fg='green')} ✅"
        )

    except Exception as e:
        click.echo(f"Something went wrong ❌: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()

```

# src\core.py

```python
from pathlib import Path
from typing import List, Tuple

from pathspec import PathSpec

from src.utils import get_file_extension, is_binary_file, should_exclude


def generate_tree(root_path: Path, pathspec: PathSpec, max_size_mb: float = 1) -> str:
    """
    Generate a tree visualization of the directory structure starting from the root path.

    Args:
        root_path: Path object representing the root directory to start from
        pathspec: PathSpec object for pattern matching
        max_size_mb: Maximum file size in megabytes to include in the tree

    Returns:
        String containing the ASCII tree representation of the directory structure
    """
    tree_str = [str(root_path.name)]

    def add_to_tree(path: Path, prefix: str = "", is_last: bool = True):
        if should_exclude(path, pathspec, max_size_mb):
            return

        # prepare the appropriate prefix for this item
        marker = "└─ " if is_last else "├─ "
        tree_str.append(f"{prefix}{marker}{path.name}")

        if path.is_dir():
            # get all valid items in directory
            items = [
                p
                for p in sorted(path.iterdir())
                if not should_exclude(p, pathspec, max_size_mb)
            ]

            # prepare the prefix for children
            new_prefix = prefix + ("    " if is_last else "│   ")

            # recursively add each item
            for i, item in enumerate(items):
                is_last_item = i == len(items) - 1
                add_to_tree(item, new_prefix, is_last_item)

    # process all root level items
    root_items = [
        p
        for p in sorted(root_path.iterdir())
        if not should_exclude(p, pathspec, max_size_mb)
    ]

    for i, path in enumerate(root_items):
        add_to_tree(path, "", i == len(root_items) - 1)

    return "\n".join(tree_str)


def process_file(file_path: Path, root_path: Path, stats: dict) -> Tuple[str, bool]:
    """
    Process a single file and generate its markdown representation with appropriate code fencing.

    Args:
        file_path: Path to the file being processed
        root_path: Root directory path, used to generate relative paths
        stats: Dictionary to track processing statistics

    Returns:
        Tuple containing:
            - String: Markdown representation of the file
            - Boolean: True if file was successfully processed, False if skipped/error
    """
    rel_path = file_path.relative_to(root_path)
    content = []

    # add file header
    content.append(f"\n# {rel_path}\n")

    # check if file is binary
    if is_binary_file(file_path):
        content.append("```plaintext")
        content.append("<!-- binary file contents omitted -->")
        content.append("```")
        stats["skipped_files"] += 1
        stats["skipped_file_list"].append(str(rel_path))
        return "\n".join(content), False

    # get appropriate language for code fence
    lang = get_file_extension(file_path)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()
            content.append(f"```{lang}")
            content.append(file_content)
            content.append("```")
        return "\n".join(content), True
    except UnicodeDecodeError:
        # handle files that looked like text but aren't
        content.append("```plaintext")
        content.append("<!-- file contents omitted: encoding error -->")
        content.append("```")
        stats["skipped_files"] += 1
        stats["skipped_file_list"].append(str(rel_path))
        return "\n".join(content), False


def generate_markdown(
    root_path: Path,
    pathspec: PathSpec,
    max_size_mb: float = 1,
) -> Tuple[str, dict]:
    """
    Generate the complete markdown document containing tree and file contents.

    Args:
        root_path: Path object representing the root directory to process
        pathspec: PathSpec object for pattern matching
        max_size_mb: Maximum file size in megabytes to include in the output

    Returns:
        Tuple containing:
            - String: The complete markdown document
            - Dict: Processing statistics
    """
    # start with project tree
    content = ["# PROJECT TREE\n"]
    content.append(generate_tree(root_path, pathspec, max_size_mb))

    # track some statistics
    stats = {
        "processed_files": 0,
        "skipped_files": 0,
        "total_size": 0,
        "processed_file_list": [],
        "skipped_file_list": [],  # New list to track skipped files
    }

    def process_directory(path: Path) -> List[str]:
        if should_exclude(path, pathspec, max_size_mb):
            if path.is_file():
                stats["skipped_files"] += 1
                stats["skipped_file_list"].append(str(path.relative_to(root_path)))
            return []

        dir_content = []
        if path.is_file():
            file_content, success = process_file(path, root_path, stats)
            if success:
                stats["processed_files"] += 1
                stats["total_size"] += path.stat().st_size
                stats["processed_file_list"].append(str(path.relative_to(root_path)))
            dir_content.append(file_content)
        else:
            for item in sorted(path.iterdir()):
                dir_content.extend(process_directory(item))

        return dir_content

    # process all files
    content.extend(process_directory(root_path))

    return "\n".join(content), stats

```

# src\defaults.py

```python
DEFAULT_CONFIG = {
    "exclude": [
        # common things to ignore
        "__pycache__",
        "node_modules",
        ".git",
        "venv",
        ".venv",
        ".env",
        ".env.*",
        ".idea",
        ".vscode",
        "dist",
        "build",
        ".next",
        "coverage",
        # foldup-related
        "codebase.md",
        ".foldignore",
        "foldup.yaml",
    ],
    "max_file_size_mb": 1,
    "include_binary_files": False,
    "show_processed_files": False,
    "estimate_tokens": False,
}

```

# src\utils.py

```python
from pathlib import Path

import tiktoken
import yaml
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from src.defaults import DEFAULT_CONFIG


def get_estimated_token_count(text: str, model: str = "gpt-4") -> int:
    """
    Estimate the number of tokens in a text string.

    Args:
        text: The text to analyze
        model: The model to use for tokenization (default: gpt-4)

    Returns:
        Estimated token count
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
        return len(encoding.encode(text))
    except Exception as e:
        print(f"Warning: Could not estimate tokens: {str(e)}")
        return 0


def get_file_extension(file_path: Path) -> str:
    """
    Get the appropriate markdown code block language for a given file.

    Args:
        file_path: Path object representing the file

    Returns:
        String representing the markdown code block language
    """
    EXTENSION_MAP = {
        # programming Languages
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".rs": "rust",
        ".go": "go",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        # web
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        # data & config
        ".md": "markdown",
        ".yml": "yaml",
        ".yaml": "yaml",
        ".json": "json",
        ".toml": "toml",
        ".ini": "ini",
        ".xml": "xml",
        # shell & scripts
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".fish": "fish",
        ".ps1": "powershell",
        # default for unknown extensions
        "": "plaintext",
    }

    # handle dotfiles (like .gitignore, .prettierrc)
    if file_path.name.startswith("."):
        return EXTENSION_MAP.get(file_path.name, "plaintext")

    return EXTENSION_MAP.get(file_path.suffix.lower(), "plaintext")


def read_config(config_path: Path, root_path: Path) -> dict:
    """
    Read and parse configuration from config file and .foldignore.

    Args:
        config_path: Path to the configuration file
        root_path: Path to the root directory (for .foldignore)

    Returns:
        Dictionary containing merged configuration settings
    """
    config = DEFAULT_CONFIG.copy()

    # Get all patterns - both from defaults and .foldignore
    patterns = []

    # Add default exclude patterns
    patterns.extend(config["exclude"])

    # Add patterns from .foldignore
    ignore_file = root_path / ".foldignore"
    if ignore_file.exists():
        try:
            with open(ignore_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        patterns.append(line)
        except Exception as e:
            print(f"warning: error reading .foldignore: {e}")

    # Create PathSpec with all patterns
    config["pathspec"] = PathSpec.from_lines(GitWildMatchPattern, patterns)

    # Read user config if it exists
    if config_path.exists():
        try:
            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                if user_config:
                    # If user config has additional exclude patterns, add them
                    if "exclude" in user_config:
                        config["pathspec"] = PathSpec.from_lines(
                            GitWildMatchPattern, patterns + user_config["exclude"]
                        )
                    # Update other config values
                    config.update(user_config)
        except Exception as e:
            print(f"warning: error reading config file: {e}")

    return config


def should_exclude(path: Path, pathspec: PathSpec, max_size_mb: float = 1) -> bool:
    """
    Determine if a path should be excluded based on patterns and size.

    Args:
        path: Path to check
        pathspec: PathSpec object for pattern matching
        max_size_mb: Maximum file size in megabytes

    Returns:
        Boolean indicating if the path should be excluded
    """
    # Convert to relative path string for matching
    str_path = str(path)

    # Check if path matches any ignore pattern
    if pathspec.match_file(str_path):
        return True

    # check file size if it's a file
    if path.is_file() and path.stat().st_size > (max_size_mb * 1024 * 1024):
        return True

    return False


def is_binary_file(file_path: Path) -> bool:
    """
    Check if a file is binary by reading its first few thousand bytes.

    Args:
        file_path: Path to the file to check

    Returns:
        Boolean indicating if the file appears to be binary
    """
    try:
        chunk_size = 8000
        with open(file_path, "rb") as file:
            content = file.read(chunk_size)

        textchars = bytearray(
            {7, 8, 9, 10, 12, 13, 27} | set(range(0x20, 0x100)) - {0x7F}
        )
        is_binary_string = bool(content.translate(None, textchars))
        return is_binary_string
    except Exception:
        return True  # if we can't read the file, assume it's binary

```

# Taskfile.yml

```yaml
# https://taskfile.dev

version: "3"

env:
  SRC_FOLDER: ./src
  TEST_FOLDER: ./tests

tasks:
  default:
    cmds:
      - task --list-all

  list:
    cmds:
      - task --list-all

  lint:
    cmds:
      - uv run ruff check $SRC_FOLDER $TEST_FOLDER

  format:
    cmds:
      - uv run ruff format $SRC_FOLDER

```