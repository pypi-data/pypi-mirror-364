# py-humantime

[![PyPI version](https://img.shields.io/pypi/v/py-humantime.svg?style=flat-square)](https://pypi.org/project/py-humantime/)
[![Build Status](https://github.com/Avishekdevnath/py-humantime/actions/workflows/ci.yml/badge.svg)](https://github.com/Avishekdevnath/py-humantime/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready Python package and CLI tool to convert between seconds and human-readable time strings.

## Features
- Convert seconds to human-readable time (e.g., `1h 2m 3s`)
- Convert human-readable time to seconds (e.g., `1h 2m 3s` → `3723`)
- Simple, extensible, and dependency-free
- Usable as both a CLI tool and Python module
- Helpful error messages and input validation
- Fully tested and ready for PyPI/GitHub

## Installation

```bash
pip install py-humantime
```

## Development install

```bash
pip install .
```

## CLI Usage

Convert seconds to human-readable:
```bash
py-humantime --to-human 4523        # → 1h 15m 23s
```
Convert human-readable to seconds:
```bash
py-humantime --to-seconds "1h 15m"  # → 4500
```

## Python Usage

```python
from pyhumantime import seconds_to_human, human_to_seconds

print(seconds_to_human(4523))          # → '1h 15m 23s'
print(human_to_seconds("1h 15m 23s"))  # → 4523
```

## Error Handling Example

```python
from pyhumantime import human_to_seconds

try:
    print(human_to_seconds('notatime'))
except ValueError as e:
    print('Error:', e)
```

## Extensibility
- The core logic is OOP-based and can be extended to support new units (e.g., milliseconds, days) by subclassing or enhancing `HumanTimeConverter` in `pyhumantime/core.py`.

## Contributing
Pull requests and issues are welcome! Please add tests for new features or bug fixes.

## License
MIT License
