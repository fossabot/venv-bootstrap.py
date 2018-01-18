import click
import sys
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

    errors = 0

    def info(msg):
        if not args["quiet"]:
            click.secho(msg)

    def warn(msg):
        click.secho("warning: {}".format(msg), fg='yellow')

    def error(msg):
        nonlocal errors
        errors += 1
        click.secho("error: {}".format(msg), fg='red')

    if not args["dir"]:
        warn("no directories supplied")

    errors = 0

    for i in args["dir"]:
        installer = Installer(i)

        installer.maybe_install(
            no_upgrade=args["no_upgrade"],
            downgrade=args["downgrade"],
            force=args["force"],
            confirm_cb=None if args["no_interactive"] else lambda msg: click.confirm(msg),
            info_cb=info,
            warn_cb=warn,
            error_cb=error
        )

    if errors:
        sys.exit(1)
