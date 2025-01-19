from pathlib import Path

import click

from src.foldup.core import generate_markdown
from src.foldup.utils import get_estimated_token_count, print_version, read_config


@click.command()
@click.argument("path", type=click.Path(exists=True), default=".")
@click.option(
    "-v",
    "--version",
    is_flag=True,
    callback=print_version,
    expose_value=False,
    is_eager=True,
    help="Show version and exit",
)
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
    "-ms",
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
    "-et",
    "--estimate-tokens",
    is_flag=True,
    default=False,
    help="Estimate tokens in output (default: False)",
)
@click.option(
    "-t",
    "--tree-only",
    is_flag=True,
    default=False,
    help="Only generate the project tree and not the file contents (default: False)",
)
def main(
    path: str,
    output: str,
    config: str,
    max_size: float,
    show_files: bool,
    estimate_tokens: bool,
    tree_only: bool,
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
        if tree_only:
            config_data["tree_only"] = True

        # generate the markdown
        click.echo(f"Processing directory: {root_path}")
        content, stats = generate_markdown(
            root_path,
            config_data["pathspec"],
            config_data["max_file_size_mb"],
            config_data.get("tree_only", False),
        )

        # write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        # calculate output file size
        output_size = output_path.stat().st_size / 1024  # size in KB

        # print to terminal
        if tree_only:
            click.echo(
                "\n⚠️  The --tree-only flag is set, only the "
                "project tree will be generated. ⚠️"
            )
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
