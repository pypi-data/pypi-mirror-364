# VoilaData
A versatile Python library to read various file formats into a pandas DataFrame, with robust handling of deeply nested data structures.

This package provides a single, convenient class `DataFrameReader` that automatically detects the file type from its extension and uses the best method to load it into a pandas DataFrame. For nested formats like JSON and YAML, it automatically flattens the data into a wide, easy-to-use format.

## Key Features

- **Simple Interface**: A single `read()` method for all supported file types.
- **Wide Format Support**: Handles a large variety of common data file formats.
- **Intelligent Flattening**: Converts deeply nested JSON and YAML into a flat, wide DataFrame.
- **Extensible**: Easily add support for more file types.

## Supported Formats

- `.csv`, `.tsv`
- `.xls`, `.xlsx`
- `.json`, `.ndjson`
- `.yaml`, `.yml`
- `.toml`
- `.parquet`
- `.orc`
- `.feather`
- `.avro`
- `.html`
- `.dta` (Stata)
- `.sav` (SPSS)


## Usage

Using the `DataFrameReader` is straightforward.

```python
from voiladata import DataFrameReader

# 1. Initialize the reader with a file path
reader = DataFrameReader('path/to/your/data.csv')

# 2. Read the file into a pandas DataFrame
df = reader.read()

print(df.head())
```

### Reading Nested JSON

The real power comes when dealing with nested data. Consider this JSON file (`data.json`):

```json
[
    {
        "id": "user1",
        "profile": {
            "name": "Alice",
            "age": 30
        },
        "logins": [
            {"timestamp": "2024-01-10T10:00:00Z", "ip": "192.168.1.1"},
            {"timestamp": "2024-01-11T12:30:00Z", "ip": "192.168.1.2"}
        ]
    }
]
```

`DataFrameReader` will automatically flatten it:

```python
from voiladata import DataFrameReader

# Read the nested JSON
reader = DataFrameReader('data.json')
df = reader.read()

# The resulting DataFrame is wide and flat
print(df)
```

**Output:**

| id    | profile_name | profile_age | logins_0_timestamp      | logins_0_ip | logins_1_timestamp      | logins_1_ip |
|:------|:-------------|:------------|:------------------------|:------------|:------------------------|:------------|
| user1 | Alice        | 30          | 2024-01-10T10:00:00Z | 192.168.1.1 | 2024-01-11T12:30:00Z | 192.168.1.2 |


## License

This project is licensed under the MIT [License](LICENSE).````