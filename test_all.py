import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Note: this is not intended as an exhaustive test suite but
# rather as a smoke test.
# Also, any bugfixes should include a dedicated test to verify the fix

#####################################################################

# This is a heavily stripped down version of subprocess.run to be usable with Python 3.4


class CompletedProcess(object):
    def __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def subprocess_run(*popenargs, **kwargs):
    with subprocess.Popen(*popenargs, **kwargs) as process:
        try:
            stdout, stderr = process.communicate()
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
    return CompletedProcess(process.args, retcode, stdout, stderr)

#####################################################################


class FirstTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._example1_dir = os.path.join(os.path.dirname(__file__), 'example1')

        cls._tempdir = tempfile.TemporaryDirectory()
        SCRIPT = 'venv-bootstrap.py'
        shutil.copy(os.path.join(os.path.dirname(__file__), SCRIPT), cls._tempdir.name)
        cls._script = os.path.join(cls._tempdir.name, SCRIPT)

    @classmethod
    def tearDownClass(cls):
        cls._tempdir.cleanup()

    def test_example1_exists(self):
        self.assertTrue(os.path.isdir(self._example1_dir))
        self.assertTrue(os.path.isfile(os.path.join(self._example1_dir, 'setup.py')))

    def _run_script(self, args):
        return subprocess_run(
            [sys.executable, self._script] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def test_example1_success(self):
        MESSAGE = b'stdout message'
        for count, count_arg in [(1, []), (1, ['--count', '1']), (2, ['--count', '2']), (0, ['--count', '0'])]:
            er = self._run_script(['venv_bootstrap_py_example1', self._example1_dir, 'succeed'] + count_arg + [MESSAGE])
            self.assertEqual(er.returncode, 0)
            self.assertEqual(er.stdout, b''.join(count * [MESSAGE, b'\n']))

    def test_example1_fail(self):
        MESSAGE = b'stderr message'
        CODE = 42
        er = self._run_script(['venv_bootstrap_py_example1', self._example1_dir, 'fail', '--message', MESSAGE, '--code', str(CODE)])
        self.assertEqual(er.returncode, CODE)
        self.assertTrue(er.stderr.endswith(MESSAGE + b'\n'))
        self.assertEqual(er.stdout, b'')

    def test_example1_pip_install_error(self):
        er = self._run_script(['some_module', os.path.devnull])
        self.assertEqual(er.returncode, 2)
        self.assertEqual(er.stdout, b'')

    def test_example1_ImportError(self):
        MODULE = b'some_non_existent_module'
        er = self._run_script([MODULE, self._example1_dir])
        self.assertEqual(er.returncode, 2)
        self.assertTrue(b'\nerror: ' in er.stderr)
        self.assertTrue(MODULE in er.stderr)
        self.assertEqual(er.stdout, b'')
