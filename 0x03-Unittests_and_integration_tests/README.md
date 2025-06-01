# Unit Tests and Integration Tests

This project contains unit tests and integration tests for various Python modules. The tests are written using Python's unittest framework and the parameterized library for test parameterization.

## Files

- `utils.py`: Contains utility functions for accessing nested maps, making HTTP requests, and memoization
- `test_utils.py`: Contains unit tests for the utility functions

## Requirements

- Python 3.7
- Ubuntu 18.04 LTS
- pycodestyle 2.5
- parameterized
- requests

## Usage

To run the tests:
```bash
python3 -m unittest test_utils.py
```

To check code style:
```bash
pycodestyle utils.py test_utils.py
``` 