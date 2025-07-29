import tomli
import os

def _get_version():
    pyproject_path = os.path.join(os.path.dirname(__file__), '..', '..', 'pyproject.toml')
    pyproject_path = os.path.abspath(pyproject_path)
    with open(pyproject_path, 'rb') as f:
        data = tomli.load(f)
    return data['project']['version']

__version__ = _get_version()
