import os
import shutil
import subprocess
import sys
import tempfile
import unittest

# Note: this is not intended as an exhaustive test suite but
# rather as a smoke test.
# Also, any bugfixes should include a dedicated test to verify the fix

VERBOSE_SUBPROCESS = os.environ.get("VERBOSE_SUBPROCESS")


class CompletedProcess(object):
    # This is a heavily stripped down version of subprocess.CompletedProcess to be usable with Python 3.4
    def __init__(self, args, returncode, stdout=None, stderr=None):
        self.args = args
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


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
        def convert(i):
            if isinstance(i, str):
                return i
            if isinstance(i, bytes):
                return i.decode()
            return str(i)

        args = [sys.executable, self._script] + [convert(i) for i in args]

        with subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        ) as process:
            try:
                stdout, stderr = process.communicate()
            except:
                process.kill()
                process.wait()
                raise
            retcode = process.poll()

        if VERBOSE_SUBPROCESS:
            print(args, ' -> ', retcode)
            print("=== stdout: ==\n", stdout)
            print("=== stderr: ==\n", stderr)

        return CompletedProcess(process.args, retcode, stdout, stderr)

    def test_example1_success(self):
        MESSAGE = 'stdout message'
        for count, count_arg in [(1, []), (1, ['--count', '1']), (2, ['--count', '2']), (0, ['--count', '0'])]:
            er = self._run_script(['venv_bootstrap_py_example1', self._example1_dir, 'succeed'] + count_arg + [MESSAGE])
            self.assertEqual(er.returncode, 0)
            self.assertEqual(er.stdout, ''.join(count * [MESSAGE, '\n']))

    def test_example1_fail(self):
        MESSAGE = 'stderr message'
        CODE = 42
        er = self._run_script(['venv_bootstrap_py_example1', self._example1_dir, 'fail', '--message', MESSAGE, '--code', CODE])
        self.assertEqual(er.returncode, CODE)
        self.assertTrue(er.stderr.endswith(MESSAGE + '\n'))
        self.assertEqual(er.stdout, '')

    def test_example1_pip_install_error(self):
        # note: a uuid is used as something that should not be installable by pip
        er = self._run_script(['some_module', '05da04ff-f259-4f09-889b-f9a41daa1703'])
        self.assertEqual(er.returncode, 2)
        self.assertEqual(er.stdout, '')

    def test_example1_ImportError(self):
        MODULE = 'some_non_existent_module'
        er = self._run_script([MODULE, self._example1_dir])
        self.assertEqual(er.returncode, 2)
        self.assertTrue('\nerror: ' in er.stderr)
        self.assertTrue(MODULE in er.stderr)
        self.assertEqual(er.stdout, '')
