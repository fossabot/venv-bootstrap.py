import click
import sys


@click.group(no_args_is_help=False)
def cli():
    """a simple Click-based application"""


@cli.command()
@click.option('--message', help="message to print")
@click.option('--code', default=1, metavar="N", show_default=True, help="exit code to return")
def fail(message, code):
    """optionally print a message to stderr and exit with failure code"""

    if message:
        click.echo(message, err=True)

    sys.exit(code)


@cli.command()
@click.argument('message')
@click.option('-c', '--count', default=1, help="repeat the message specified numer of times")
def succeed(message, count):
    """print the specified message and exit with 0 exit code"""

    for i in range(count):
        click.echo(message)
