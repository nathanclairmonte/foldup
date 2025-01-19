# foldup

A command-line tool that "folds" your codebase into a single Markdown file that can be easily passed to LLMs.

The output `codebase.md` file includes:
1. Your project tree
2. The filepath and contents of each file in the codebase

Here's an example of what the output looks like for a very simple project:

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

Now you should be able to run `foldup` from anywhere in your system! Please let me know if anything doesn't work though.

## Usage

```bash
# Process current directory
foldup .

# Process specific directory
foldup /path/to/project
```

## Configuration

You can configure Foldup with command-line flags, a config file, or a `.foldignore` file.

### Command-line Flags
| Flag | Description | Default |
| --- | --- | --- |
| `-v, --version` | Print version | |
| `-o, --output` | Custom output filename | `codebase.md` |
| `-c, --config` | Custom config filename | `foldup.yaml` |
| `-sf, --show-files` | Include list of processed files in output | `False` |
| `-et, --estimate-tokens` | Estimate token count | `False` |
| `-t, --tree-only` | Only generate the project tree | `False` |
| `-ms, --max-size` | Maximum file size in MB to process | `2.0` |

### Config File (default: `foldup.yaml`)

Create a `foldup.yaml` config file in your project root to customize the behavior of Foldup. This example config file shows all the default settings. You can specify a custom config file with the `-c` flag.

```yaml
# Default config
exclude:
  # common files to exclude
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
max_file_size_mb: 2.0
show_processed_files: false
estimate_tokens: false
```

### `.foldignore` File

You can also configure foldup to ignore certain directories or files by creating a `.foldignore` file in your project root. The syntax is the same as `.gitignore`.

```
# Example .foldignore
*.log
temp/
*.pyc
.DS_Store
```

## Estimated Token Count

The estimated token count can be optionally displayed by passing the `--estimate-tokens` flag. Foldup uses the [tiktoken](https://github.com/openai/tiktoken) library to estimate token count. Remember that this is just an estimate, the actual token count may vary (but probably not by an insane amount).


> **N.B.** Tiktoken uses the GPT-4 tokenizer. For ChatGPT, it should be relatively close. For Claude, it could be off by ±20%.


## Development

These steps require that you have the [UV project manager](https://docs.astral.sh/uv/getting-started/installation/) installed.

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
uv run python -m src.foldup.cli
```
