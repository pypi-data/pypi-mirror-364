# tests/test_version.py

from importlib.metadata import version


from src import agix


def test_package_version_matches():
    assert agix.__version__ == version("agix")
