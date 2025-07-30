from setuptools import setup, find_packages

setup(
    name='voiladata',
    version='1.0.1',
    author='Debrup Mukherjee',
    packages=find_packages(),
    install_requires=[
        "pandas>=1.5.0",
    ],
)