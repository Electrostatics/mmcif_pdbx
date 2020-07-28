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
from pdbx import PdbxSyntaxError

from pdbx.reader import PdbxReader
from pdbx import loads as read_cifstr

DATA_DIR = Path("tests/data")
LOGGER = logging.getLogger()


@pytest.mark.parametrize("input_cif", ["1kip.cif", "1ffk.cif"], ids=str)
def test_data_file(input_cif):
    """Test data file input."""
    input_path = DATA_DIR / Path(input_cif)
    with open(input_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        data_list = []
        reader.read(data_list)


@pytest.mark.parametrize("input_cif", ["1kip-sf.cif"], ids=str)
def test_structure_factor_file(input_cif):
    """Test structure factor input."""
    input_path = DATA_DIR / Path(input_cif)
    with open(input_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        container_list = []
        reader.read(container_list)
    container = container_list[0]
    refln_object = container.get_object("refln")
    assert refln_object is not None


def test_empty_file():
    assert read_cifstr("") == []


def test_empty_data_block():
    assert read_cifstr("data_test")[0].get_object_name_list() == []


def test_missing_value_eof():
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test _a.x")
    assert "end of file" in str(excinfo.value)


def test_missing_value_not_eof():
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test _a.x _a.y A")
    assert "Missing data for item _a.x" in str(excinfo.value)


def test_missing_key():
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test _a.x A B")
    assert "Unrecognized syntax element: B" in str(excinfo.value)


def test_empty_loop_header_eof():
    # formal CIF 1.1 grammar expects at least one tag
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test loop_")
    assert "end of file" in str(excinfo.value)


def test_empty_loop_header_not_eof():
    # formal CIF 1.1 grammar expects at least one tag
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test loop_ loop_")
    assert "Unexpected token" in str(excinfo.value)


def test_empty_loop_body_eof():
    # formal CIF 1.1 grammar expects at least one value
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test loop_ _a.x")
    assert "loop_ without values" in str(excinfo.value)


def test_empty_loop_body_not_eof():
    # formal CIF 1.1 grammar expects at least one value
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test loop_ _a.x loop_")
    assert "Unexpected reserved word" in str(excinfo.value)


def test_loop_value_count_mismatch():
    # https://www.iucr.org/resources/cif/spec/version1.1/cifsyntax § 63:
    # The number of values in the body must be a multiple of the number of
    # tags in the header
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test loop_ _a.x _a.y A")
        pytest.skip("does not raise yet")  # TODO


def test_incomplete_multiline_string():
    read_cifstr("data_test _a.x\n;A\n;")  # correct (terminated)
    read_cifstr("data_test _a.x ;A")  # correct (not a multi-line string)
    with pytest.raises(PdbxSyntaxError) as excinfo:
        read_cifstr("data_test _a.x\n;A")
    assert "unterminated multi-line" in str(excinfo.value)
