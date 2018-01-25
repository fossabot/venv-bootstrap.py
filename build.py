from pybuilder.core import use_plugin, init, Author

use_plugin("pypi:pybuilder_scm_ver_plugin")
use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
#use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("filter_resources")

name = "venv-bootstrap.py"
default_task = "publish"

authors = [Author("Kyrylo Shpytsya", "kshpitsa@gmail.com")]
license = "MIT"
summary = 'a portable and streamlined version of "python -m venv <env> && <env>/bin/pip install <install>" && <env>/bin/python -m <module> ..."'
url = "https://github.com/kshpytsya/venv-bootstrap.py"


@init
def set_properties(project):
    project.depends_on('atomicwrites>=1.1.5,<2')
    project.depends_on('click', '==6.*')

    project.set_property('flake8_break_build', True)
    project.set_property('flake8_include_test_sources', True)
    project.set_property('flake8_include_scripts', True)
    project.set_property('flake8_max_line_length', 130)
    project.set_property('flake8_ignore', 'E402')

    project.include_file("venv_bootstrap", "res/venv-bootstrap.py")

    project.set_property('distutils_entry_points', {'console_scripts': ['venv-bootstrap-install=venv_bootstrap.cli:main']})
    project.set_property('filter_resources_glob', ['**/venv_bootstrap/__init__.py'])
    project.set_property("distutils_classifiers", [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Build Tools'
    ])
