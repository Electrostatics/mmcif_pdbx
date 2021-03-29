import re
import pdbx
from pdbx import __version__


def test_version_exists():
    assert hasattr(pdbx, "__version__")


def test_version():
    assert re.match(r"[0-9]+\.[0-9]+\.[0-9]+", __version__)
    print(f"VERSION: {__version__}")
