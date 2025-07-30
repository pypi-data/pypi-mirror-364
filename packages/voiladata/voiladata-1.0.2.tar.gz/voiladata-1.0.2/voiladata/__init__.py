"""
DataFrame Loader
================

A versatile Python library to read various file formats into a pandas DataFrame, 
with robust handling of nested data structures.
"""

__version__ = "1.0.2"

from .main import DataFrameReader, DataFrameHealthChecker

__all__ = ["DataFrameReader", "DataFrameHealthChecker"]