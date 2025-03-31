#!/usr/bin/env python3
"""
Command-line interface for running the Script Runner web application.
"""

import os
import click


@click.command()
@click.option(
    "--config",
    envvar="CONFIG_FILE_PATH",
    help="Path to the configuration file.",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
@click.option(
    "--host",
    required=True,
    help="Host to bind to.",
)
@click.option(
    "--port",
    required=True,
    help="Port to bind to.",
    type=int,
)
def main(config, host, port, debug):
    """Run the Script Runner web application."""
    os.environ["CONFIG_FILE_PATH"] = config

    from app.app import app

    click.echo(f"Starting Script Runner on {host}:{port} with config {config}")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
