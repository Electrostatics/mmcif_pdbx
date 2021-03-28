import re
import pdbx
from importlib import metadata


def test_version_exists():
    assert hasattr(pdbx, "__version__")


def test_version():
    assert re.match(r"[0-9]+\.[0-9]+\.[0-9]+", metadata.version("mmcif-pdbx"))
    assert re.match(r"[0-9]+\.[0-9]+\.[0-9]+", metadata.version("mmcif_pdbx"))
    print(f"VERSION1: {metadata.version('mmcif_pdbx')}")
    print(f"VERSION2: {metadata.version('mmcif-pdbx')}")
