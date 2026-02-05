from setuptools import setup, find_packages

setup(
    name="darabase",
    version="0.1",
    description="MySql orm for python",
    install_requires=[
        "SqlAlchemy",
    ],
    py_modules=["database"],
)