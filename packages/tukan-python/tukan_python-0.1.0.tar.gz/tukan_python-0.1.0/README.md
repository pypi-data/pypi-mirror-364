# tukan_python

A Python package to interact with the TukanMX API, retrieve table metadata, and build and execute queries with flexible filters, groupings, and aggregations.

## Installation

Once the package is published to PyPI, install it using:

```bash
pip install tukan_python
```

## Usage

### Authentication

You need an API token to use the TukanMX API. You can provide it directly to the `Tukan` or `Query` classes, or set it as an environment variable:

```bash
export API_TUKAN=your_api_token
```

### Main Classes

#### Tukan
Handles authentication and requests to the TukanMX API. Provides methods for retrieving tables, indicators, and metadata, as well as sending and receiving data.

```python
from tukan_python.tukan import Tukan

tukan = Tukan(token="your_api_token")

# Retrieve metadata for a table
metadata = tukan.get_table_metadata("table_name")

# Retrieve a list of tables
all_tables = tukan.get_tables()

# Retrieve a list of indicators
indicators = tukan.get_indicators()
```

#### Query
Helper class for building and executing queries against the TukanMX API. Supports filters, groupings, aggregations, and execution.

```python
from tukan_python.query import Query

# Create a Query instance
query = Query("table_name", token="your_api_token")

# Add filters, groupings, or aggregations as needed
query.set_where([{ "reference": "column", "eq": "value" }])
query.set_group_by([{ "reference": "column" }])
query.set_aggregate([{ "indicator": "indicator_name", "operation": "sum" }])

# Execute the query
result = query.execute_query()
print(result["df"])  # result is a dict with 'indicators' and a pandas DataFrame
```

#### Utility Functions

- `create_identity_query_for_table(table_name, language)`
- `create_identity_query_for_table_with_date_filters(table_name, language, from_date, to_date)`
- `create_query_from_query_id_or_name(query_id_or_name)`
- `create_query_from_payload(payload)`

These functions help build queries quickly from table names, IDs, or payloads.

## License
See the `LICENSE` file for license information.

---

For more details, see the code in `tukan_python/tukan.py` and `tukan_python/query.py`.
