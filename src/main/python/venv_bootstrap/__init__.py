__version__ = '${version}'

if __version__[0] == '$':
    # running from non installed sources, probably unittests
    import setuptools_scm
    __version__ = setuptools_scm.get_version()
