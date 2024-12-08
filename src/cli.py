from pathlib import Path

import click

from src.core import generate_markdown
from src.utils import read_config


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
    default="fold.yaml",
    help="Config file path (default: fold.yaml)",
)
@click.option(
    "--max-size",
    type=float,
    default=1.0,
    help="Maximum file size in MB to process (default: 1.0)",
)
@click.option(
    "--show-files",
    is_flag=True,
    default=False,
    help="Include list of processed files in output (default: False)",
)
def main(
    path: str, output: str, config: str, max_size: float, show_files: bool
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
        exclude_patterns = set(config_data.get("exclude", []))

        # override config values with command line options
        if max_size != 1.0:
            config_data["max_file_size_mb"] = max_size
        if show_files:
            config_data["show_processed_files"] = True

        # generate the markdown
        click.echo(f"Processing directory: {root_path}")
        content, stats = generate_markdown(
            root_path,
            exclude_patterns,
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
        if show_files:
            click.echo("\nFiles processed:")
            for file_path in sorted(stats["processed_file_list"]):
                click.echo(f"- {file_path}")
        click.echo(f"\nOutput written to: {output_path}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
