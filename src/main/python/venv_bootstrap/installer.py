import os
import pkg_resources
import re
from atomicwrites import atomic_write
from . import __version__

SCRIPT_UUID = b"2ca11a4f-5d89-4cc9-bb4c-f50f65c62119"
SCRIPT_FNAME = "venv-bootstrap.py"
VERSION = pkg_resources.parse_version(__version__)
MAX_READ = 1000000


def _nop_msg_cb(msg):
    pass


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

        if not os.path.lexists(self.fname):
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

    def maybe_install(
        self,
        *,
        check_result=None,
        no_upgrade=False,
        downgrade=False,
        force=False,
        confirm_cb=None,
        info_cb=_nop_msg_cb,
        warn_cb=_nop_msg_cb,
        error_cb=_nop_msg_cb
    ):
        if check_result is None:
            check_result = self.check()

        def should_install():
            if check_result == 'absent':
                info_cb('installing into "{}"'.format(self.path))
                return True

            if check_result == 'version-same':
                info_cb('already installed in "{}"'.format(self.path))
                return False

            if check_result == 'no-dir':
                error_cb('directory "{}" does not exist'.format(self.path))
                return False

            if check_result == 'a-dir':
                error_cb('target "{}" exists and is a directory'.format(self.fname))
                return False

            MAP = {
                'read-error': 'non-readable file "{}"',
                'a-link': 'existing symlink "{}"',
                'not-our': '"{}" missing our signature',
                'version-unknown': '"{}" missing version info',
                'version-same-modified': '"{}" having the same version but modified contents',
            }

            if check_result in MAP:
                what = MAP[check_result].format(self.fname)
                if force:
                    warn_cb('overwriting {}'.format(what))
                    return True

                if confirm_cb:
                    if confirm_cb('overwrite {} ?'.format(what)):
                        info_cb('installing into "{}"'.format(self.path))
                        return True
                    else:
                        info_cb('skipping installation into "{}"'.format(self.path))
                        return False

                error_cb('cowardly refusing to overwrite {}'.format(what))
                return False

            if check_result == 'version-older':
                if no_upgrade:
                    info_cb('not upgrading existing "{}"'.format(self.fname))
                    return False
                else:
                    info_cb('upgrading existing "{}"'.format(self.fname))
                    return True

            if check_result == 'version-newer':
                nonlocal downgrade
                if not downgrade and confirm_cb:
                    downgrade = confirm_cb('downgrade existing "{}" ?'.format(self.fname))

                if downgrade:
                    info_cb('downgrading existing "{}"'.format(self.fname))
                    return True
                else:
                    info_cb('not downgrading existing "{}"'.format(self.fname))
                    return False

            assert 0, "unknown check result: {}".format(check_result)

        decision = should_install()
        assert decision is not None
        if decision:
            self.install()

    def install(self):
        with atomic_write(self.fname, mode='wb', overwrite=True) as f:
            f.write(self.get_script())
