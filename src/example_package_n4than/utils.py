from pathlib import Path

import tiktoken
import yaml
from pathspec import PathSpec
from pathspec.patterns import GitWildMatchPattern

from src.example_package_n4than.defaults import DEFAULT_CONFIG


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
