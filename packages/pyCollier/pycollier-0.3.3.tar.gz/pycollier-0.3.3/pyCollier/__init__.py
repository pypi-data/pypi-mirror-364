from .frontend import *

__doc__ = """
Python interface for [COLLIER Fortran library](https://collier.hepforge.org/). 

## Installation

Go to main directory and type
```bash
pip install .
```

## Usage
After installation, you should be able to load `pyCollier` via
```python
import pyCollier
```
Then you can calculate loop functions e.g. via
```python
print(pyCollier.A0(125**2))
```
"""

initialize()