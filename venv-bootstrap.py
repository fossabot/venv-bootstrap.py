#################################################################################
#
#  MIT License
#
#  Copyright (c) 2018 Kyrylo Shpytsya
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#################################################################################

# This file can be obtained as
#
#    https://github.com/kshpytsya/venv-bootstrap.py/raw/master/venv-bootstrap.py
#
# and executed as
#
#    python3 venv-bootstrap.py ...

import sys

if sys.version_info < (3, 5):
    sys.exit("Sorry, venv-bootstrap.py requires at least Python 3.5")

import argparse
import os
import runpy
import signal
import subprocess
import venv


class EnvBuilder(venv.EnvBuilder):
    def ensure_directories(self, env_dir):
        self.last_context = super().ensure_directories(env_dir)
        return self.last_context

    def setup_scripts(self, context):
        pass


env_var_venv = os.environ.get('VENV_BOOTSTRAP_PY_ENV')
default_venv_prefix = os.path.join(os.path.dirname(__file__), '.venv.')
default_venv_for_display = default_venv_prefix + "<module>"

parser = argparse.ArgumentParser(
    description='a portable and streamlined version of '
                '"python -m venv <env> && <env>/bin/pip install <install>" && <env>/bin/python -m <module> ..."',
)
parser.add_argument(
    'module',
    help='python module name to execute'
)
parser.add_argument(
    'install',
    help='quoted string to be parsed with "shlex.split" and passed as "pip install" parameters'
)
parser.add_argument(
    '--venv', metavar='PATH',
    help='venv directory path, relative to venv-bootstrap.py. '
         'Note: can be overriden by VENV_BOOTSTRAP_PY_ENV environment variable (default: "{}")'.format(default_venv_for_display)
)
parser.add_argument(
    '--verbose', action='store_true',
    help="give more output"
)
parser.add_argument(
    '--pip-verbosity',
    metavar="N",
    type=int,
    default=0,
    help='number of -v options to pass to "pip", including via "ensurepip" (default: %(default)s)'
)
parser.add_argument(
    '--fail-code',
    metavar="N",
    type=int,
    default=2,  # this is the same code used by argparse to report parsing errors
    help="exit code to return in case of failure to execute a module as opposed to the exit code "
         "caused by module execution (default: %(default)s)"
)
parser.add_argument(
    'args',
    metavar='...',
    nargs=argparse.REMAINDER,
    help='arguments and options to pass to the module. Prepend with "--" to pass anything starting with "-"'
)
parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)

args = parser.parse_args()

if args.child:
    def error(msg=None):
        if msg:
            sys.stderr.writelines(["error: ", msg, "\n"])

        sys.exit(args.fail_code)

    def info(msg):
        if args.verbose:
            sys.stderr.write(msg)

    def run_and_exit():
        old_argv = sys.argv
        try:
            sys.argv = ["python -m {}".format(args.module)] + args.args
            runpy.run_module(args.module, run_name='__main__')
            # should the module forget to do sys.exit()
            sys.exit(0)
        finally:
            sys.argv = old_argv

    try:
        run_and_exit()
    except ImportError:
        pass

    info('Failed to find "{}", trying to install using "pip"\n'.format(args.module))

    pip_verbose = ['--verbose'] * args.pip_verbosity

    do_bootstrap = False
    try:
        import pip
    except ImportError:
        do_bootstrap = True

    if do_bootstrap:
        # note: do not do this in exception handler to avoid confusing "exception while
        # handling exception" kinds of tracebacks

        info('Bootstrapping "pip" using "ensurepip"\n')

        # note: ensurepip cannot be executed in-process, as it imports pip from
        # a temporary copy of a wheel which is destroyed upon return, leaving
        # no non-hackish ways of using pip afterwards.
        subprocess.check_call([sys.executable, '-m', 'ensurepip', '--altinstall'] + pip_verbose)

        import pip  # noqa

    import shlex

    if pip.main(pip_verbose + ['install'] + shlex.split(args.install)):
        error()

    try:
        run_and_exit()
    except ImportError as e:
        error("{}".format(e))

else:
    if env_var_venv:
        args.venv = env_var_venv
    elif args.venv is None:
        args.venv = default_venv_prefix + args.module

    builder = EnvBuilder(symlinks=os.name != 'nt')
    builder.create(args.venv)
    signal.signal(signal.SIGINT, lambda n, s: None)
    sys.exit(subprocess.call([builder.last_context.env_exe, __file__, '--child'] + sys.argv[1:]))
