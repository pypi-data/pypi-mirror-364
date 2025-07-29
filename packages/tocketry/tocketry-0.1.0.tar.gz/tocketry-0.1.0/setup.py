import sys

sys.stderr.write("""
Unsupported installation method: python setup.py
Please use `python -m pip install .` instead.
""")
# sys.exit(1)
from setuptools import setup

setup(
    name="tocketry",
    install_requires=["python-dateutil"],
)
