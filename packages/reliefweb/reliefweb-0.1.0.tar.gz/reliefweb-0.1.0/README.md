# ReliefWeb Python Library

A Python client library for the [ReliefWeb API](https://apidoc.reliefweb.int/).

## Installation

```bash
pip install .
```

## Usage

```python
from reliefweb.client import ReliefWebClient

# Initialize client
client = ReliefWebClient()

# Fetch reports
reports = client.get_reports(
    filters={"country": {"eq": "ETH"}},
    fields=["id", "date", "title"],
    sort=[{"date": "desc"}],
    limit=5,
    offset=0,
    presets=None
)
print("Reports:", reports)

# Fetch jobs
jobs = client.get_jobs(
    filters={"status": {"eq": "active"}},
    fields=["id", "title", "date"],
    sort=[{"date": "desc"}],
    limit=5
)
print("Jobs:", jobs)

# Fetch training
training = client.get_training(
    filters=None,
    fields=["id", "title", "date"],
    sort=[{"date": "desc"}],
    limit=5
)
print("Training:", training)
```

### ReliefWebClient Methods

#### `get_reports(filters=None, fields=None, sort=None, limit=10, offset=0, presets=None)`
Fetch reports from ReliefWeb API.
- `filters` (dict, optional): Filtering parameters (e.g., `{ "country": { "eq": "ETH" } }`).
- `fields` (list, optional): Fields to include in results (e.g., `["id", "date", "title"]`).
- `sort` (list, optional): Sorting options (e.g., `[{"date": "desc"}]`).
- `limit` (int, optional): Number of results to return.
- `offset` (int, optional): Offset for pagination.
- `presets` (list, optional): Presets to apply (e.g., `["expat"]`).
- **Returns:** dict (API response)

#### `get_jobs(filters=None, fields=None, sort=None, limit=10, offset=0, presets=None)`
Fetch jobs from ReliefWeb API.
- Parameters and return value are the same as `get_reports`.

#### `get_training(filters=None, fields=None, sort=None, limit=10, offset=0, presets=None)`
Fetch training events from ReliefWeb API.
- Parameters and return value are the same as `get_reports`.

#### Constructor: `ReliefWebClient(api_key=None)`
Initialize the client. If you have an API key, pass it as `api_key`.

## Running Tests

To run the unit tests, use:

```bash
python -m unittest tests/test_client.py
```

## Features
- Simple interface for ReliefWeb API endpoints
- Handles authentication and pagination

## License
MIT
