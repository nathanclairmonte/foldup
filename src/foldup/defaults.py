DEFAULT_CONFIG = {
    "exclude": [
        # common files to exclude
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
    ],
    "max_file_size_mb": 2.0,
    "show_processed_files": False,
    "estimate_tokens": False,
}
