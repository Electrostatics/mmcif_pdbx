"""PDBx/mmCIF Python dictionary resources.

All of the code in this repository is original based on
http://mmcif.wwpdb.org/. Specifically, this code is directly derived from the
`pdbx code <http://mmcif.wwpdb.org/docs/sw-examples/python/src/pdbx.tar.gz>`_
linked from
`PDBx Python Parser Examples and Tutorial
 <http://mmcif.wwpdb.org/docs/sw-examples/python/html/>`_.

See `PDBx Python Parser Examples and Tutorial
 <http://mmcif.wwpdb.org/docs/sw-examples/python/html/>`_ for more information
about this package, including examples.
"""

# import pdbx.reader
import io
from importlib import metadata
from .reader import PdbxReader
from .writer import PdbxWriter
from .errors import PdbxSyntaxError, PdbxError  # noqa: F401
from .containers import DataCategory, DataContainer  # noqa: F401

__version__ = metadata.version("mmcif-pdbx")


def load(fp) -> list:
    """Parse a CIF file.

    :param file fp:  file object ready for reading
    :returns:  a list of :class:`~pdbx.containers.DataContainer` objects
    """
    data = []
    PdbxReader(fp).read(data)
    return data


def loads(s) -> list:
    """Parse a CIF string.

    :param str s:  string with CIF data
    :returns: a list of :class:`~pdbx.containers.DataContainer` objects
    """
    return load(io.StringIO(s))


def dump(datacontainers, fp):
    """Write a list of objects to a CIF file.

    :param list datacontainers:  a list of :class:`~pdbx.containers.DataContainer` objects # noqa E501
    :param file fp:  a file object ready for writing
    """
    PdbxWriter(fp).write(datacontainers)


def dumps(datacontainers) -> str:
    """Serialize a list of objects to a CIF-formatted string.

    :param list datacontainers:  list of :class:`~pdbx.containers.DataContainer` objects # noqa E501
    :returns:  CIF-formatted string
    """
    fp = io.StringIO()
    dump(datacontainers, fp)
    return fp.getvalue()
