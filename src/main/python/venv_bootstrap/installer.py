import os
import pkg_resources
import re
from . import __version__

SCRIPT_UUID = b"2ca11a4f-5d89-4cc9-bb4c-f50f65c62119"
SCRIPT_FNAME = "venv-bootstrap.py"
VERSION = pkg_resources.parse_version(__version__)
MAX_READ = 1000000


class Installer:
    _script = None

    def __init__(self, path):
        self.path = path
        self.fname = os.path.join(path, SCRIPT_FNAME)

    @classmethod
    def get_script(cls):
        if cls._script is None:
            cls._script = \
                pkg_resources.resource_string(__name__, 'res/' + SCRIPT_FNAME) \
                .replace(b'@@@VERSION@@@', __version__.encode()) \
                .replace(b'@@@UUID@@@', SCRIPT_UUID)

        return cls._script

    def check(self):
        if not os.path.isdir(self.path):
            return 'no-dir'

        if os.path.isdir(self.fname):
            return 'a-dir'

        if not os.path.exists(self.fname):
            return 'absent'

        if os.path.islink(self.fname):
            return 'a-link'

        try:
            with open(self.fname, 'rb') as f:
                contents = f.read(MAX_READ)
        except: # noqa
            return 'read-error'

        if SCRIPT_UUID not in contents:
            return 'not-our'

        version_strs = re.findall(b'^VERSION = "(.*)"$', contents, re.MULTILINE)

        if len(version_strs) != 1:
            return 'version-unknown'

        version = pkg_resources.parse_version(version_strs[0].decode(errors='ignore'))

        if version > VERSION:
            return 'version-newer'

        if version < VERSION:
            return 'version-older'

        self.get_script()

        if contents == self._script:
            return 'version-same'

        return 'version-same-modified'

    @staticmethod
    def decide(check_result, *, upgrade=False):
        pass

    def install(self):
        tmp_fname = os.path.join(self.path, '.{}.{}'.format(SCRIPT_FNAME, os.getpid()))
        with open(tmp_fname, "wb") as f:
            f.write(self.get_script())
        os.rename(tmp_fname, self.fname)
