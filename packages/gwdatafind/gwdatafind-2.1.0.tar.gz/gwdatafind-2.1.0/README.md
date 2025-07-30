# GWDataFind

The GWDataFind data discovery client.

The GWDataFind service allows users to query for the location of
Gravitational-Wave Frame (GWF) files containing data from the current
gravitational-wave detectors.

[![PyPI version](https://badge.fury.io/py/gwdatafind.svg)](http://badge.fury.io/py/gwdatafind)
[![Conda version](https://img.shields.io/conda/vn/conda-forge/gwdatafind.svg)](https://anaconda.org/conda-forge/gwdatafind/)
[![License](https://img.shields.io/pypi/l/gwdatafind.svg)](https://choosealicense.com/licenses/gpl-3.0/)
[![Documentation status](https://readthedocs.org/projects/gwdatafind/badge/?version=latest)](https://gwdatafind.readthedocs.io/en/latest/?badge=latest)

## Installation

The simplest installation is via `pip`:

```bash
python -m pip install gwdatafind
```

This package is also available as a Conda package:

```bash
conda install -c conda-forge gwdatafind
```

## Basic Usage

To find the URLs of all `H1_R` files for the LIGO-Hanford observatory in
a given GPS interval:

```python
>>> from gwdatafind import find_urls
>>> find_urls('H', 'H1_R', 1198800018, 1198800618)
```

To utillise connection pooling, create a `Session`:

```python
>>> from gwdatafind import (find_urls, Session)
>>> with Session() as sess:
...     for ifo in ("H", "L"):
...         urls[ifo] = find_urls(
...             ifo,
...             f"{ifo}1_R",
...             1198800018,
...             1198800618,
...             session=sess,
...         )

## On the command-line

GWDataFind can also be executed via the command-line client, for full details
run

```bash
$ python -m gwdatafind --help
```

For more documentation, see <https://gwdatafind.readthedocs.io/>.
