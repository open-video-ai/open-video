"""Backwards-compat shim.

All project metadata lives in pyproject.toml. This file exists so legacy
workflows keep working:

    pip install .                 # uses pyproject.toml (preferred)
    pip install -e .              # editable install
    python setup.py --version     # legacy introspection
"""
from setuptools import setup

setup()
