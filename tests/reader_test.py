##
# File:    readerTests.py
# Author:  jdw
# Date:    9-Jan-2012
# Version: 0.001
#
# Update:
#  27-Sep-2012  jdw add test case for reading PDBx structure factor file 
#
##
"""Test cases for reading PDBx/mmCIF data files reader class."""
import logging
from pathlib import Path
import pytest
from pdbx.reader.reader import PdbxReader


DATA_DIR = Path("tests/data")
LOGGER = logging.getLogger()


@pytest.mark.parametrize("input_cif", ["1kip.cif", "1ffk.cif"], ids=str)
def test_data_file(input_cif): 
    """Read a small data file."""
    input_path = DATA_DIR / Path(input_cif)
    with open(input_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        data_list = []
        reader.read(data_list)


@pytest.mark.parametrize("input_cif", ["1kip-sf.cif"], ids=str)
def test_structure_factor_file(input_cif):
    input_path = DATA_DIR / Path(input_cif)
    with open(input_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        container_list = []
        reader.read(container_list)
    container = container_list[0]
    refln_object = container.get_object("refln")
    assert(refln_object is not None)
