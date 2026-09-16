import click

from bintools.cli.commands import import_binset


@click.group()
def cli():
    pass


cli.add_command(import_binset)

if __name__ == "__main__":
    cli()
