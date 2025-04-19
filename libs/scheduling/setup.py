from setuptools import setup, find_packages

setup(
    name="scheduling",
    version="0.1.0",
    packages=find_packages(),  # picks up scheduler.py, feasibility_checker.py, etc.
)