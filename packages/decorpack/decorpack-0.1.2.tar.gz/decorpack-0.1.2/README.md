# Decorpack

[![PyPI](https://img.shields.io/pypi/v/decorpack)](https://pypi.org/project/decorpack/)  

A small collection of reusable Python decorators and utilities for logging, timing, singletons, and safe‑exception handling.

## Features
 
- `logger`: pre-configured Python logger ready to use 
- `singleton`: decorator  and metaclass for enforcing single-instance class
- `timer`: decorator to measure function runtime 
- `try_except`: decorator for catching & handling exceptions cleanly

## Installation

```bash
  pip install decorpack
```

## Quickstart

```python
from decorpack.logger import log

log.info("Quickstart over!")
```
```python
from decorpack.timer import timer

@timer
def expensive_computation(x):
    pass
```
```python
from decorpack.singleton import singleton

@singleton
class MyConfig:
    pass
```
```python
from decorpack.try_except import try_except

@try_except(ValueError)
def parse_int(s: str) -> int:
    return int(s)
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
