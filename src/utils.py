from pathlib import Path
from typing import Set

import tiktoken
import yaml

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

    # handle dotfiles (like .gitignore, .env)
    if file_path.name.startswith("."):
        return EXTENSION_MAP.get(file_path.name, "plaintext")

    return EXTENSION_MAP.get(file_path.suffix.lower(), "plaintext")


def read_foldignore(root_path: Path) -> Set[str]:
    """
    Read .foldignore file if it exists and return patterns to ignore.

    Args:
        root_path: Path to the directory containing .foldignore

    Returns:
        Set of patterns to ignore
    """
    ignore_file = root_path / ".foldignore"
    ignore_patterns = set()

    if ignore_file.exists():
        try:
            with open(ignore_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        ignore_patterns.add(line)
        except Exception as e:
            print(f"warning: error reading .foldignore: {e}")

    return ignore_patterns


def read_config(config_path: Path, root_path: Path) -> dict:
    """
    Read and parse configuration from config file and .foldignore.

    Args:
        config_path: Path to the configuration file
        root_path: Path to the root directory (for .foldignore)

    Returns:
        Dictionary containing merged configuration settings
    """

    # merge .foldignore patterns with defaults
    foldignore_patterns = read_foldignore(root_path)
    DEFAULT_CONFIG["exclude"].extend(foldignore_patterns)

    if not config_path.exists():
        return DEFAULT_CONFIG

    try:
        with open(config_path) as f:
            user_config = yaml.safe_load(f)

        # if user config has exclude patterns, merge with .foldignore
        if user_config.get("exclude"):
            user_config["exclude"].extend(foldignore_patterns)

        return {**DEFAULT_CONFIG, **user_config}
    except Exception as e:
        print(f"warning: error reading config file: {e}")
        return DEFAULT_CONFIG


def should_exclude(
    path: Path, exclude_patterns: Set[str], max_size_mb: float = 1
) -> bool:
    """
    Determine if a path should be excluded based on patterns and size.

    Args:
        path: Path to check
        exclude_patterns: Set of patterns to exclude
        max_size_mb: Maximum file size in megabytes

    Returns:
        Boolean indicating if the path should be excluded
    """
    # check patterns
    str_path = str(path)
    if any(pattern in str_path for pattern in exclude_patterns):
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
