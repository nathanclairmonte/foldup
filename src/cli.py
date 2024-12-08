from pathlib import Path

import click

from .core import generate_markdown
from .utils import read_config


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
def main(path: str, output: str, config: str, max_size: float) -> None:
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
        config_data = read_config(config_path)
        exclude_patterns = set(config_data.get("exclude", []))

        # override max file size if specified in command
        if max_size != 1.0:  # only override if user specified a different value
            config_data["max_file_size_mb"] = max_size

        # generate the markdown
        click.echo(f"Processing directory: {root_path}")
        content = generate_markdown(
            root_path, exclude_patterns, config_data["max_file_size_mb"]
        )

        # write output
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)

        click.echo(f"Successfully generated: {output_path}")

    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    main()
