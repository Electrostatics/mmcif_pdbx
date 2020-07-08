"""PDBx/mmCIF Python dictionary resources.

All of the code in this repository is based on http://mmcif.wwpdb.org/.
Specifically, this code is directly derived from
http://mmcif.wwpdb.org/docs/sw-examples/python/src/pdbx.tar.gz linked from
http://mmcif.wwpdb.org/docs/sw-examples/python/html/.

See http://mmcif.wwpdb.org/docs/sw-examples/python/html/ for more information
about this package, including examples.
"""


def load(fp) -> list:
    """Parse a CIF file into a list of DataContainer objects"""
    from .reader import PdbxReader
    data = []
    PdbxReader(fp).read(data)
    return data


def loads(s: str) -> list:
    """Parse a CIF string into a list of DataContainer objects"""
    import io
    return load(io.StringIO(s))


def dump(datacontainers: list, fp):
    """Write a list of DataContainer objects to a CIF file"""
    from .writer import PdbxWriter
    PdbxWriter(fp).write(datacontainers)


def dumps(datacontainers: list) -> str:
    """Serialize a list of DataContainer objects to a CIF formatted string"""
    import io
    fp = io.StringIO()
    dump(datacontainers, fp)
    return fp.getvalue()
