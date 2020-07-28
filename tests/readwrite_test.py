##
# File:    PdbxReadWriteTests.py
# Author:  jdw
# Date:    9-Oct-2011
# Version: 0.001
#
# Updated:
#         24-Oct-2012 jdw update path details and reorganize.
#
##
"""Test reading, writing, and updating files."""
import logging
from pathlib import Path
import pdbx
from pdbx.reader import PdbxReader
from pdbx.writer import PdbxWriter
from pdbx import DataCategory, DataContainer


_LOGGER = logging.getLogger()
DATA_DIR = Path("tests/data")


def test_init_write_read(tmp_path):
    """Test initialization, writing, and reading."""
    attribute_name_list = [
        "aOne",
        "aTwo",
        "aThree",
        "aFour",
        "aFive",
        "aSix",
        "aSeven",
        "aEight",
        "aNine",
        "aTen",
    ]
    row_list = [
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ]
    category_name = "category"
    container = DataContainer("myblock")
    category = DataCategory(category_name, attribute_name_list, row_list)
    category.print_it()
    container.append(category)
    container.print_it()
    container_list = [container]
    cif_path = Path(tmp_path) / Path("test-simple.cif")
    with open(cif_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(container_list)
    container_list = []
    with open(cif_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        reader.read(container_list)
    for container in container_list:
        for object_name in container.get_object_name_list():
            name, attr_list, row_list = container.get_object(object_name).get()
            _LOGGER.info("Recovered data category  %s\n", name)
            _LOGGER.info("Attribute list           %r\n", repr(attr_list))
            _LOGGER.info("Row list                 %r\n", repr(row_list))


def test_update_data_file(tmp_path):
    """Test updating of a data file."""
    container = DataContainer("myblock")
    category = DataCategory("pdbx_seqtool_mapping_ref")
    category.append_attribute("ordinal")
    category.append_attribute("entity_id")
    category.append_attribute("auth_mon_id")
    category.append_attribute("auth_mon_num")
    category.append_attribute("pdb_chain_id")
    category.append_attribute("ref_mon_id")
    category.append_attribute("ref_mon_num")
    category.append([9, 2, 3, 4, 5, 6, 7])
    category.append([10, 2, 3, 4, 5, 6, 7])
    category.append([11, 2, 3, 4, 5, 6, 7])
    category.append([12, 2, 3, 4, 5, 6, 7])
    container.append(category)
    data_list = [container]
    cif_path = Path(tmp_path) / Path("test-output-1.cif")
    with open(cif_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(data_list)
    data_list = []
    with open(cif_path, "rt") as input_file:
        reader = PdbxReader(input_file)
        reader.read(data_list)
    block = data_list[0]
    block.print_it()
    category = block.get_object("pdbx_seqtool_mapping_ref")
    category.print_it()
    for irow in range(category.row_count):
        category.set_value("some value", "ref_mon_id", irow)
        category.set_value(100, "ref_mon_num", irow)
    cif_path = Path(tmp_path) / Path("test-output-2.cif")
    with open(cif_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(data_list)


def test_read_write_data_file(tmp_path):
    """Data file read/write test."""
    input_path = Path(DATA_DIR) / Path("1kip.cif")
    with open(input_path, "rt") as input_file:
        data_list = pdbx.load(input_file)
    output_path = Path(tmp_path) / Path("testOutputDataFile.cif")
    with open(output_path, "wt") as output_path:
        pdbx.dump(data_list, output_path)


# TODO: 2020/07/16 intendo - are the spaces at the end of the line needed
#       for testing or should they be removed to make flake8 happy?
ROUNDTRIPPABLE_CIF_STR = """data_foo
#
#
_cat1.key1  123
_cat1.key2  12.3
_cat1.key3  unquoted
##
_cat2.key1  "quoted string"
_cat2.key2  
;muli line
string
;

_cat2.key3  "  leadingspace"
_cat2.key4  "trailingspace  "
_cat2.key5  'embedded " double-quote space'
_cat2.key6  "embedded ' single-quote space"
##
loop_
_cat3.nullvalues
_cat3.strings
.           "."      
?           "?"      
##
"""


def test_roundtrip():
    containers = pdbx.loads(ROUNDTRIPPABLE_CIF_STR)
    assert pdbx.dumps(containers) == ROUNDTRIPPABLE_CIF_STR
