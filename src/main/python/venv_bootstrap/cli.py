import click
from .installer import Installer


@click.command()
@click.version_option()
@click.option('--quiet', is_flag=True, help='omit info messages')
@click.option('--no-upgrade', is_flag=True, help='do not upgrade existing venv-bootstrap.py files')
@click.option('--downgrade', is_flag=True, help='downgrade existing files to this version')
@click.option('--force', is_flag=True, help='override existing venv-bootstrap.py files that do not look like our file')
@click.option('--no-interactive', is_flag=True, help='disable prompts')
@click.argument('dir', nargs=-1, type=click.Path(exists=True, file_okay=False, resolve_path=True))
def main(**args):
    """install venv-bootstrap.py script into specified directories"""
    def info(msg):
        if not args["quiet"]:
            click.secho(msg, bold=True)

    if not args["dir"]:
        info("warning: no directories supplied")

    for i in args["dir"]:
        installer = Installer(i)

        check_result = installer.check()

        info("{}: {}".format(installer.fname, check_result))

        if args["force"]:
            installer.install()
