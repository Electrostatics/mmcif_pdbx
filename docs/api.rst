===============
 API Reference
===============

The API of :mod:`pdbx` is documented here for developers to use its mmCIF/PDBx functionality.

.. Note::

   The API is still changing and there is currently no guarantee that
   it will remain stable between minor releases.

.. currentmodule:: pdbx

.. module:: pdbx

Input/Output functions
----------------------

.. autosummary::
   :toctree: api

   load
   loads
   dump
   dumps

Input/Output data structures
----------------------------
.. autosummary::
   :toctree: api

   containers
   reader
   writer

Error classes
-------------
.. autosummary::
   :toctree: api

   errors