##
# File:    writerTests.py
# Author:  jdw
# Date:    3-November-2009
# Version: 0.001
#
# Update:
#  5-Apr-2011 jdw   Using the double quote format preference
# 24-Oct-2012 jdw   Update path and examples.
##
"""Test PDBx/mmCIF write and formatting operations."""
import logging
from pathlib import Path
from pdbx.containers import DataContainer, DataCategory
from pdbx.writer import PdbxWriter


_LOGGER = logging.getLogger()


def test_write_data_file(tmp_path):
    """Test case -  write data file."""
    output_path = Path(tmp_path) / Path("test-output.cif")
    category = DataCategory("pdbx_seqtool_mapping_ref")
    category.append_attribute("ordinal")
    category.append_attribute("entity_id")
    category.append_attribute("auth_mon_id")
    category.append_attribute("auth_mon_num")
    category.append_attribute("pdb_chain_id")
    category.append_attribute("ref_mon_id")
    category.append_attribute("ref_mon_num")
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    category.append((1, 2, 3, 4, 5, 6, 7))
    container = DataContainer("myblock")
    container.append(category)
    data_list = [container]
    with open(output_path, "wt") as output_file:
        writer = PdbxWriter(output_file)
        writer.write(data_list)
