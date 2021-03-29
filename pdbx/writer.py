##
# File: PdbxWriter.py
# Date: 2011-10-09 Jdw Adapted from PdbxParser.py
#
# Updates:
# 5-Apr-2011 jdw Using the double quote format preference
# 23-Oct-2012 jdw update path details and reorganize.
#
###
"""Classes for writing data and dictionary containers in PDBx/mmCIF format."""
from sys import stdout
from .containers import DefinitionContainer, DataContainer
from .errors import PdbxError

__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"


MAXIMUM_LINE_LENGTH = 2048
SPACING = 2
INDENT_DEFINITION = 3
DO_DEFINITION_INDENT = False


class PdbxWriter:
    """Write PDBx data files or dictionaries.
    Use the input container or container list.
    """

    def __init__(self, output_file=stdout):
        """Initialize.

        :param file output_file:  file object ready for writing
        """
        self.__output_file = output_file
        self.__container_list = []
        self.__maximum_line_length = MAXIMUM_LINE_LENGTH
        self.__spacing = SPACING
        self.__indent_definition = INDENT_DEFINITION
        self.__indent_space = " " * self.__indent_definition
        self._do_definition_indent = DO_DEFINITION_INDENT
        # Maximum number of rows checked for value length and format
        self.__row_partition = None

    def set_row_partition(self, num_rows):
        """Maximum number of rows checked for value length and format.

        :param int num_rows:  maximum number of rows
        """
        self.__row_partition = num_rows

    def write(self, container_list):
        """Write out a list of containers.

        :param list container_list:  list of
          :class:`~pdbx.containers.ContainerBase` objects to write.
        """
        self.__container_list = container_list
        for container in self.__container_list:
            self.write_container(container)

    def write_container(self, container):
        """Write out information for an individual container.

        :param container:  container to write
        :type container:  :class:`~pdbx.containers.ContainerBase`
        """
        indent_string = " " * self.__indent_definition
        if isinstance(container, DefinitionContainer):
            self.__write("save_%s\n" % container.name)
            self._do_definition_indent = True
            self.__write(indent_string + "#\n")
        elif isinstance(container, DataContainer):
            if container.get_global():
                self.__write("global_\n")
                self._do_definition_indent = False
                self.__write("\n")
            else:
                self.__write("data_%s\n" % container.name)
                self._do_definition_indent = False
                self.__write("#\n")
        for name in container.get_object_name_list():
            obj = container.get_object(name)
            object_list = obj.row_list
            # Skip empty objects
            if not object_list:
                continue
            # Item - value formattting
            if len(object_list) == 1:
                self.__write_item_value_format(obj)
            # Table formatting
            elif len(object_list) > 1 and obj.attribute_list:
                self.__write_table_format(obj)
            else:
                raise PdbxError(
                    "len(object_list) = %d and len(obj.attribute_list) = %d"
                    % (len(object_list), len(obj.attribute_list))
                )
            if self._do_definition_indent:
                self.__write(indent_string + "#")
            else:
                self.__write("#")
        # Add a trailing saveframe reserved word
        if isinstance(container, DefinitionContainer):
            self.__write("\nsave_\n")
        self.__write("#\n")

    def __write(self, string_):
        """Write a string.

        :param str string_:  string to write
        """
        self.__output_file.write(string_)

    def __write_item_value_format(self, category):
        """Write items and values for the given category.

        :param category:  category to write
        :type category:  :class:`~pdbx.containers.DataCategory`
        """
        # Compute the maximum item name length within this category -
        attribute_name_max_length = 0
        for attribute_name in category.attribute_list:
            attribute_name_max_length = max(
                attribute_name_max_length, len(attribute_name)
            )
        item_name_max_length = (
            self.__spacing + len(category.name) + attribute_name_max_length + 2
        )
        line_list = []
        line_list.append("#\n")
        for attribute_name, _ in category.attribute_list_with_order:
            if self._do_definition_indent:
                # - add indent --
                line_list.append(self.__indent_space)
            item_name = "_%s.%s" % (category.name, attribute_name)
            line_list.append(item_name.ljust(item_name_max_length))
            line_list.append(category.get_value_formatted(attribute_name, 0))
            line_list.append("\n")
        self.__write("".join(line_list))

    def __write_table_format(self, category):
        """Write table format data.

        :param category:  category to write
        :type category:  :class:`~pdbx.containers.DataCategory`
        """
        # Write the declaration of the loop_
        line_list = []
        line_list.append("#\n")
        if self._do_definition_indent:
            line_list.append(self.__indent_space)
        line_list.append("loop_")
        for attribute_name in category.attribute_list:
            line_list.append("\n")
            if self._do_definition_indent:
                line_list.append(self.__indent_space)
            item_name = "_%s.%s" % (category.name, attribute_name)
            line_list.append(item_name)
        self.__write("".join(line_list))
        # Write the data in tabular format
        # For speed make the following evaluation on a portion of the table
        if self.__row_partition is not None:
            num_steps = max(1, category.row_count / self.__row_partition)
        else:
            num_steps = 1
        format_type_list, _ = category.get_format_type_list(steps=num_steps)
        max_length_list = category.get_max_attribute_list_length(
            steps=num_steps
        )
        spacing = " " * self.__spacing
        for irow in range(category.row_count):
            line_list = []
            line_list.append("\n")
            if self._do_definition_indent:
                line_list.append(self.__indent_space + " ")
            for iattr in range(category.attribute_count):
                format_type = format_type_list[iattr]
                max_length = max_length_list[iattr]
                if format_type in ("FT_UNQUOTED_STRING", "FT_NULL_VALUE"):
                    val = category.get_value_formatted_by_index(iattr, irow)
                    line_list.append(val.ljust(max_length))
                elif format_type == "FT_NUMBER":
                    val = category.get_value_formatted_by_index(iattr, irow)
                    line_list.append(val.rjust(max_length))
                elif format_type == "FT_QUOTED_STRING":
                    val = category.get_value_formatted_by_index(iattr, irow)
                    line_list.append(val.ljust(max_length + 2))
                elif format_type == "FT_MULTI_LINE_STRING":
                    val = category.get_value_formatted_by_index(iattr, irow)
                    line_list.append(val)
                line_list.append(spacing)
            self.__write("".join(line_list))
        self.__write("\n")
