[![Tests](https://github.com/Electrostatics/mmcif_pdbx/workflows/Tests/badge.svg)](https://github.com/Electrostatics/mmcif_pdbx/actions?query=workflow%3ATests)
[![codecov](https://codecov.io/gh/Electrostatics/mmcif_pdbx/branch/master/graph/badge.svg)](https://codecov.io/gh/Electrostatics/mmcif_pdbx)

# PDBx/mmCIF Dictionary Resources

This is yet another PyPI package for http://mmcif.wwpdb.org/pdbx-mmcif-home-page.html.  It emphasizes a simple and pure Python interface to basic mmCIF functionality.

The canonical mmCIF Python package can be found at https://github.com/rcsb/py-mmcif.  It is full-featured and includes C/C++ code to accelerate I/O functions.  

## Origin of this software
All of the code in this repository is based on http://mmcif.wwpdb.org/.
Specifically, this code is directly derived from http://mmcif.wwpdb.org/docs/sw-examples/python/src/pdbx.tar.gz linked from http://mmcif.wwpdb.org/docs/sw-examples/python/html/.

See http://mmcif.wwpdb.org/docs/sw-examples/python/html/ for more information about this package, including examples.

## Versions

Versions 0.* maintain API compatibility with the original code.
Subsequent version break that compatibility, primarily by renaming methods in compliance with PEP8.

## Installing this software

This python package can be installed via [setuptools](https://pypi.org/project/setuptools/), `pip install .`, or via [PyPI](https://pypi.org/project/mmcif-pdbx/).
