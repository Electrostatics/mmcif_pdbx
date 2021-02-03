.. -*- coding: utf-8 -*-
.. mmcif_pdbx documentation master file, created by
   sphinx-quickstart on Tue Jul  7 18:59:55 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

mmcif_pdbx
==========

This is yet another PyPI package for http://mmcif.wwpdb.org/pdbx-mmcif-home-page.html.
It emphasizes a simple and pure Python interface to basic mmCIF functionality.

The canonical mmCIF Python package can be found at https://github.com/rcsb/py-mmcif.  It is full-featured and includes C/C++ code to accelerate I/O functions.  

This package provides the module :mod:`pdbx`.
More information about the :mod:`pdbx` module can be found in the :ref:`api-label` section.

-----------------------
Origin of this software
-----------------------

All of the code in this repository is based on http://mmcif.wwpdb.org/.
Specifically, this code is directly derived from http://mmcif.wwpdb.org/docs/sw-examples/python/src/pdbx.tar.gz linked from http://mmcif.wwpdb.org/docs/sw-examples/python/html/.

See http://mmcif.wwpdb.org/docs/sw-examples/python/html/ for more information about this package, including examples.

--------
Versions
--------

Versions 0.* maintain API compatibility with the original code.
Subsequent versions break that compatibility, primarily by renaming methods in compliance with PEP8.

------------
Installation
------------

This python package can be installed via `setuptools <https://pypi.org/project/setuptools/>`_, ``pip install .``, or via `PyPI <https://pypi.org/project/mmcif-pdbx/>`_.

-------
Testing
-------

The software can be tested with `pytest <https://docs.pytest.org/en/stable/>`_ by running::

   python -m pytest

from the top-level directory.

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`

--------
Contents
--------

.. toctree::
   :maxdepth: 2

   api/index
   changelog