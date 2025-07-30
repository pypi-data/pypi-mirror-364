import json
import logging
import pandas as pd
import toml
from collections.abc import MutableMapping
from pathlib import Path
from typing import Any, Dict, List, Union

# Configure basic logging for informative output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DataFrameReader:
    """
    A comprehensive and robust class to read various file formats from a file path
    and return a pandas DataFrame. It is designed to handle both flat and
    deeply nested data structures by flattening them into a wide format.
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initializes the DataFrameReader with the file path.

        Args:
            file_path (Union[str, Path]): The path to the input file.

        Raises:
            FileNotFoundError: If the file does not exist at the given path.
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"The file was not found at path: {self.file_path}")
        self.file_extension = self.file_path.suffix.lower()

    def _flatten_data(self, data_obj: Union[Dict, List], parent_key: str = '', sep: str = '_') -> Dict:
        """
        Recursively flattens a nested dictionary or list into a single dictionary.

        Args:
            data_obj (Union[Dict, List]): The object to flatten.
            parent_key (str): The base key to use for the flattened keys.
            sep (str): The separator to use between keys.

        Returns:
            Dict: A flattened dictionary.
        """
        items: Dict[str, Any] = {}
        if isinstance(data_obj, MutableMapping):
            for k, v in data_obj.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                items.update(self._flatten_data(v, new_key, sep=sep))
        elif isinstance(data_obj, list):
            if not data_obj:
                items[parent_key] = []
            else:
                for i, v in enumerate(data_obj):
                    new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
                    items.update(self._flatten_data(v, new_key, sep=sep))
        else:
            items[parent_key] = data_obj
        return items

    def read(self, **kwargs: Any) -> pd.DataFrame:
        """
        Reads the file based on its extension and returns a DataFrame.

        This method dispatches to the appropriate reading method based on the file extension.
        Keyword arguments are passed to the underlying pandas read function.

        Args:
            **kwargs: Arbitrary keyword arguments for pandas read functions.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the file data.
        
        Raises:
            ValueError: If the file format is unsupported.
            ImportError: If a required optional dependency is not installed.
        """
        reader_map = {
            '.csv': self._read_csv,
            '.tsv': self._read_tsv,
            '.xls': self._read_excel,
            '.xlsx': self._read_excel,
            '.html': self._read_html,
            '.json': self._read_json,
            '.yaml': self._read_yaml,
            '.yml': self._read_yaml,
            '.toml': self._read_toml,
            '.ndjson': self._read_ndjson,
            '.parquet': self._read_parquet,
            '.orc': self._read_orc,
            '.feather': self._read_feather,
            '.avro': self._read_avro,
            '.dta': self._read_stata,
            '.sav': self._read_spss,
        }

        reader_func = reader_map.get(self.file_extension)

        if not reader_func:
            msg = f"Unsupported file format: '{self.file_extension}'"
            logging.error(msg)
            raise ValueError(msg)

        try:
            logging.info(f"Reading file '{self.file_path}' with extension '{self.file_extension}'...")
            return reader_func(**kwargs)
        except Exception as e:
            logging.error(f"An error occurred while reading '{self.file_path}': {e}", exc_info=True)
            raise

    def _read_csv(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_csv(self.file_path, **kwargs)

    def _read_tsv(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_csv(self.file_path, sep='\t', **kwargs)

    def _read_json(self, **kwargs: Any) -> pd.DataFrame:
        sep = kwargs.pop('sep', '_')
        with self.file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            flattened_data = [self._flatten_data(item, sep=sep) for item in data]
            return pd.DataFrame(flattened_data, **kwargs)
        elif isinstance(data, dict):
            return pd.DataFrame([self._flatten_data(data, sep=sep)], **kwargs)
        else:
            logging.warning(f"Top-level object in '{self.file_path}' is not a list or dict.")
            return pd.DataFrame()

    def _read_yaml(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import yaml
        except ImportError:
            raise ImportError("Reading YAML files requires PyYAML. Install with: pip install dataframe-loader[yaml]")
        
        sep = kwargs.pop('sep', '_')
        with self.file_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if isinstance(data, list):
            flattened_data = [self._flatten_data(item, sep=sep) for item in data]
            return pd.DataFrame(flattened_data, **kwargs)
        elif isinstance(data, dict):
            return pd.DataFrame([self._flatten_data(data, sep=sep)], **kwargs)
        else:
            logging.warning(f"Top-level object in '{self.file_path}' is not a list or dict.")
            return pd.DataFrame()

    def _read_excel(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import openpyxl
        except ImportError:
            raise ImportError("Reading Excel files requires openpyxl. Install with: pip install dataframe-loader[excel]")
        return pd.read_excel(self.file_path, **kwargs)

    def _read_arrow_format(self, read_func, format_name, extra_name, **kwargs):
        try:
            import pyarrow
        except ImportError:
            raise ImportError(f"Reading {format_name} files requires pyarrow. Install with: pip install dataframe-loader[{extra_name}]")
        return read_func(self.file_path, **kwargs)

    def _read_parquet(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_parquet, "Parquet", "arrow", **kwargs)

    def _read_orc(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_orc, "ORC", "arrow", **kwargs)

    def _read_feather(self, **kwargs: Any) -> pd.DataFrame:
        return self._read_arrow_format(pd.read_feather, "Feather", "arrow", **kwargs)

    def _read_avro(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import pyarrow.avro
        except ImportError:
            raise ImportError("Reading Avro files requires pyarrow. Install with: pip install dataframe-loader[arrow]")
        with pyarrow.avro.open_file(self.file_path, 'rb') as reader:
            return reader.read(**kwargs).to_pandas()

    def _read_toml(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import toml
        except ImportError:
            raise ImportError("Reading TOML files requires toml. Install with: pip install dataframe-loader[toml]")
        with self.file_path.open('r', encoding='utf-8') as f:
            data = toml.load(f)
        return pd.json_normalize(data, **kwargs)

    def _read_ndjson(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_json(self.file_path, lines=True, **kwargs)

    def _read_html(self, **kwargs: Any) -> pd.DataFrame:
        try:
            import lxml
        except ImportError:
            raise ImportError("Reading HTML files requires lxml. Install with: pip install dataframe-loader[html]")
        tables = pd.read_html(self.file_path, **kwargs)
        if tables:
            return tables[0]
        else:
            logging.warning(f"No tables found in HTML file: {self.file_path}")
            return pd.DataFrame()

    def _read_stata(self, **kwargs: Any) -> pd.DataFrame:
        return pd.read_stata(self.file_path, **kwargs)

    def _read_spss(self, **kwargs: Any) -> pd.DataFrame:
        try:
            return pd.read_spss(self.file_path, **kwargs)
        except ImportError:
            raise ImportError("Reading SPSS files requires pyreadstat. Install with: pip install dataframe-loader[spss]")