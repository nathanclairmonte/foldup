# src/core.py

from pathlib import Path
from typing import List, Set, Tuple

from .utils import get_file_extension, is_binary_file, should_exclude


def generate_tree(
    root_path: Path, exclude_patterns: Set[str], max_size_mb: float = 1
) -> str:
    """
    Generate a tree visualization of the directory structure starting from the root path.

    Args:
        root_path: Path object representing the root directory to start from
        exclude_patterns: Set of patterns used to determine which files/directories to exclude
        max_size_mb: Maximum file size in megabytes to include in the tree

    Returns:
        String containing the ASCII tree representation of the directory structure
    """
    tree_str = [str(root_path.name)]

    def add_to_tree(path: Path, prefix: str = "", is_last: bool = True):
        if should_exclude(path, exclude_patterns, max_size_mb):
            return

        # prepare the appropriate prefix for this item
        marker = "└─ " if is_last else "├─ "
        tree_str.append(f"{prefix}{marker}{path.name}")

        if path.is_dir():
            # get all valid items in directory
            items = [
                p
                for p in sorted(path.iterdir())
                if not should_exclude(p, exclude_patterns, max_size_mb)
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
        if not should_exclude(p, exclude_patterns, max_size_mb)
    ]

    for i, path in enumerate(root_items):
        add_to_tree(path, "", i == len(root_items) - 1)

    return "\n".join(tree_str)


def process_file(file_path: Path, root_path: Path) -> Tuple[str, bool]:
    """
    Process a single file and generate its markdown representation with appropriate code fencing.

    Args:
        file_path: Path to the file being processed
        root_path: Root directory path, used to generate relative paths

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
        return "\n".join(content), False


def generate_markdown(
    root_path: Path, exclude_patterns: Set[str], max_size_mb: float = 1
) -> str:
    """
    Generate a complete markdown document containing the directory tree and all file contents.

    Args:
        root_path: Path object representing the root directory to process
        exclude_patterns: Set of patterns used to determine which files/directories to exclude
        max_size_mb: Maximum file size in megabytes to include in the output

    Returns:
        String containing the complete markdown document with:
            - Project tree visualization
            - Contents of all processed files
            - Processing statistics
    """
    # start with project tree
    content = ["# PROJECT TREE\n"]
    content.append(generate_tree(root_path, exclude_patterns, max_size_mb))

    # track some statistics
    stats = {"processed_files": 0, "skipped_files": 0, "total_size": 0}

    def process_directory(path: Path) -> List[str]:
        if should_exclude(path, exclude_patterns, max_size_mb):
            return []

        dir_content = []
        if path.is_file():
            file_content, success = process_file(path, root_path)
            if success:
                stats["processed_files"] += 1
                stats["total_size"] += path.stat().st_size
            else:
                stats["skipped_files"] += 1
            dir_content.append(file_content)
        else:
            for item in sorted(path.iterdir()):
                dir_content.extend(process_directory(item))

        return dir_content

    # process all files
    content.extend(process_directory(root_path))

    # add statistics footer
    content.append("\n# PROCESSING STATISTICS\n")
    content.append(f"- Files processed: {stats['processed_files']}")
    content.append(f"- Files skipped: {stats['skipped_files']}")
    content.append(f"- Total size processed: {stats['total_size'] / 1024:.1f} KB")

    return "\n".join(content)
