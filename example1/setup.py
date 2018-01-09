from setuptools import setup, find_packages

setup(
    name='venv-bootstrap.py-example1',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    # entry_points='''
    #     [console_scripts]
    #     venv-bootstrap.py-example1=venv_bootstrap_py_example1:cli
    # ''',
)
