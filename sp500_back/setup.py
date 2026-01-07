from setuptools import setup

setup(
    name="sp500_back",
    version="0.1",
    description="S&P 500 stock analysis , back end for python",
    install_requires=[
        "fastapi",
        "uvicorn[standard]",
    ],
    py_modules=["sp500_back"],
)