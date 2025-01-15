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
