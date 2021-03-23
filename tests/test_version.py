import re
import pdbx
from pdbx import __version__, config


def test_version_exists():
    assert hasattr(pdbx, "__version__")


def test_version():
    assert re.match(r"[0-9]+\.[0-9]+", __version__) or __version__.startswith(
        "0+untagged"
    )
    assert re.match(
        r"[0-9]+\.[0-9]+", config.VERSION
    ) or config.VERSION.startswith("0+untagged")
    assert __version__ == config.VERSION
