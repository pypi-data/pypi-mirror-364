from setuptools import setup, find_packages

# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='voiladata',
    version='1.0.2',
    author='Debrup Mukherjee',
    author_email='dmukherjeetextiles@gmail.com',  
    description='A versatile Python library to read various file formats into a pandas DataFrame, and perform basic data health checks.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/Dmukherjeetextiles/VoilaData', 
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires='>=3.8', # Recommended: Specify Python versions
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.20.0" # numpy is used in main.py
    ],
    extras_require={
        "excel": ["openpyxl"],
        "yaml": ["PyYAML"],
        "toml": ["toml"],
        "html": ["lxml"],
        "arrow": ["pyarrow"],
        "spss": ["pyreadstat"],
        "all": [
            "openpyxl",
            "PyYAML",
            "toml",
            "lxml",
            "pyarrow",
            "pyreadstat"
        ]
    }
)