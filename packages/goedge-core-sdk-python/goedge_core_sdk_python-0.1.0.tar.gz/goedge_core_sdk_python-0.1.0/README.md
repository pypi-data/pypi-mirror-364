# GoEdge Core SDK Python Wrapper

This project provides a Python wrapper for the GoEdge Core C SDK. It uses `ctypes` to interface with the C library, allowing Python applications to leverage the functionality of the GoEdge ecosystem.

## Project Structure

- `goedge/`: Contains the Python wrapper module.
  - `core.py`: The main wrapper file that uses `ctypes` to call the C SDK functions.
- `goedge-core-sdk-c/`: Contains the C source code for the core SDK.
- `pyproject.toml`: Poetry project configuration file.

## Installation

To use this wrapper, you first need to compile the C SDK into a shared library (e.g., `libge-core.so` on Linux). Then, you can install the Python package using Poetry:

```bash
poetry install
```

## Usage

```python
from goedge import core

# Initialize the core SDK
core.core_init("my_module", 2, core.LOG_LEVEL_INFO)

# ... use other SDK functions ...

# Exit the core SDK
core.core_exit()
```
