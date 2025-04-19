from setuptools import setup, find_packages

setup(
    name="scheduling",
    version="0.1.0",
    packages=find_packages(),  # picks up scheduler.py, feasibility_checker.py, etc.
    install_requires=[
      "Flask>=2.0",                     # for the feasibility blueprint
      "mysql-connector-python>=8.0",    # for your DB calls
      "pygad>=2.16",                    # the GA you’re using
      "pandas>=1.3", 
      "Jinja2>=3.0",
      "SQLAlchemy>=1.4",                   
    ],
)