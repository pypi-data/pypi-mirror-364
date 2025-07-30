import click
import kenjyco_libs


@click.command()
def main():
    """Clone missing repos and install more packages in editable mode"""
    kenjyco_libs.dev_setup()
