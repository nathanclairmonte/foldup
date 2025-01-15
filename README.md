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
