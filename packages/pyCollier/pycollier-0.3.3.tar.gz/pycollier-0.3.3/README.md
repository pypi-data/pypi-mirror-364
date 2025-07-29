# pyCollier

[![pipeline status](https://gitlab.com/anybsm/pycollier/badges/master/pipeline.svg)](https://gitlab.com/anybsm/pycollier/commits/master) 
[![coverage report](https://gitlab.com/anybsm/pycollier/badges/master/coverage.svg)](https://gitlab.com/anybsm/pycollier/commits/master)

Python interface for [COLLIER Fortran library](https://collier.hepforge.org/). Not all COLLIER functions are available yet. Please [open an issue](https://gitlab.com/anybsm/pycollier/-/issues) if you want any specific function to be implemented.

### The pyCollier team

pyCollier is developed by Henning Bahl, Johannes Braathen, Martin Gabelmann, and Georg Weiglein.

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
pyCollier.A0(125**2)
```

## API documentation

A detailed API documentation is available [here](https://anybsm.gitlab.io/pycollier).

## Dockerimage
To build a docker image run the following from within the repositories root directory:
```bash
docker build -t pycollier .
```
Example usage: 
```bash
docker run --rm pycollier python -c 'from pyCollier import c0; print(c0(0,0,0,1,1,1))'
```

## References

Please cite 
```
@article{Denner:2016kdg,
    author = "Denner, Ansgar and Dittmaier, Stefan and Hofer, Lars",
    title = "{Collier: a fortran-based Complex One-Loop LIbrary in Extended Regularizations}",
    eprint = "1604.06792",
    archivePrefix = "arXiv",
    primaryClass = "hep-ph",
    reportNumber = "FR-PHENO-2016-003, ICCUB-16-016",
    doi = "10.1016/j.cpc.2016.10.013",
    journal = "Comput. Phys. Commun.",
    volume = "212",
    pages = "220--238",
    year = "2017"
}
```
when you use `pyCollier`.

