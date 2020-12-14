==========
Change log
==========

Unreleased
==========

* Added a change log.
  (`#42 <https://github.com/Electrostatics/mmcif_pdbx/issues/42>`_)

v1.1.2 (01-Aug-2020)
====================

Additions
---------

* Added `versioneer <https://github.com/warner/python-versioneer>`_ versioning support.
  (`#39 <https://github.com/Electrostatics/mmcif_pdbx/issues/39>`_, `#40 <https://github.com/Electrostatics/mmcif_pdbx/pull/40>`_)

* Added Sphinx API documentation and set up `readthedocs.io <http://mmcif-pdbx.readthedocs.io>`_ site.
  (`#8 <https://github.com/Electrostatics/mmcif_pdbx/issues/8>`_, `#31 <https://github.com/Electrostatics/mmcif_pdbx/pull/31>`_, `#35 <https://github.com/Electrostatics/mmcif_pdbx/issues/35>`_, `#36 <https://github.com/Electrostatics/mmcif_pdbx/pull/36>`_)

* Added de-linting to continuous integration pipeline with `psf/black <https://github.com/psf/black>`_.
  (`#37 <https://github.com/Electrostatics/mmcif_pdbx/pull/37>`_)

Changes
-------

* Flattened namespace.
  *This should have triggered a 1.2.0 release but the versioning wasn't updated correctly.*
  (`#32 <https://github.com/Electrostatics/mmcif_pdbx/pull/36>`_)

v1.1.1 (11-Jul-2020)
====================

Changes
-------

* Minor update of version number in :file:`setup.py`.

v1.1.0 (11-Jul-2020)
====================

Additions
---------

* Includes new tests.
  (`#30 <https://github.com/Electrostatics/mmcif_pdbx/pull/30>`_)

Changes
-------

* Implements new CIF I/O functions: load, loads, dump, dumps.
  (`#28 <https://github.com/Electrostatics/mmcif_pdbx/pull/28>`_, `#29 <https://github.com/Electrostatics/mmcif_pdbx/pull/29>`_)
* Improved consistency in reading and writing special characters.
  (`#21 <https://github.com/Electrostatics/mmcif_pdbx/pull/27>`_, `#27 <https://github.com/Electrostatics/mmcif_pdbx/pull/27>`_)

v1.0.0 (07-Jul-2020)
====================

Changes
-------

* Significant changes to API, including:

  * PEP8-complaint class and function naming
  * Improved :mod:`pdbx.reader` use of :class:`StopIteration`.
    (`#22 <https://github.com/Electrostatics/mmcif_pdbx/issues/22>`_, `#23 <https://github.com/Electrostatics/mmcif_pdbx/pull/23>`_)
  * Simplification of module structure.
    (`#19 <https://github.com/Electrostatics/mmcif_pdbx/pull/19>`_, `#24 <https://github.com/Electrostatics/mmcif_pdbx/issues/24>`_, `#26 <https://github.com/Electrostatics/mmcif_pdbx/pull/26>`_)
  * Removal of redundant tests and conversion of testing to pylint.

* General code de-linting.
  (`#1 <https://github.com/Electrostatics/mmcif_pdbx/issues/1>`_, `#6 <https://github.com/Electrostatics/mmcif_pdbx/issues/6>`_, `#14 <https://github.com/Electrostatics/mmcif_pdbx/pull/14>`_)

* Updates to documentation.
  (`#25 <https://github.com/Electrostatics/mmcif_pdbx/pull/25>`_)

Fixes
-----

* Fix typo in continuous integration pipeline.
  (`#17 <https://github.com/Electrostatics/mmcif_pdbx/pull/17>`_)

v0.0.1 (05-Jul-2020)
====================

Initial release.
