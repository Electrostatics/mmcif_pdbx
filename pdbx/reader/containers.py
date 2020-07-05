##
#
# File: PdbxContainers.py
# Original: 02-Feb-2009 jdw
#
# Update:
# 23-Mar-2011 jdw Added method to rename attributes in category containers.
# 05-Apr-2011 jdw Change cif writer to select double quoting as preferred
# quoting style where possible.
# 16-Jan-2012 jdw Create base class for DataCategory class
# 22-Mar-2012 jdw when append attributes to existing categories update
# existing rows with placeholder null values.
# 2-Sep-2012 jdw add option to avoid embedded quoting that might
# confuse simple parsers.
# 28-Jun-2013 jdw export remove method
# 29-Jun-2013 jdw export remove row method
##
"""

A collection of container classes supporting the PDBx/mmCIF storage model.

A base container class is defined which supports common features of
data and definition containers. PDBx data files are organized in
sections called data blocks which are mapped to data containers.
PDBx dictionaries contain definition sections and data sections
which are mapped to definition and data containes respectively.

Data in both PDBx data files and dictionaries are organized in
data categories. In the PDBx syntax individual items or data
identified by labels of the form '_categoryName.attribute_name'.
The terms category and attribute in PDBx jargon are analogous
table and column in relational data model, or class and attribute
in an object oriented data model.

The DataCategory class provides base storage container for instance
data and definition meta data.

"""
import re
from sys import stdout
import traceback


__docformat__ = "restructuredtext en"
__author__ = "John Westbrook"
__email__ = "jwest@rcsb.rutgers.edu"
__license__ = "Creative Commons Attribution 3.0 Unported"
__version__ = "V0.01"


class CifName:
    """Class of utilities for CIF-style data names."""
    @staticmethod
    def category_part(name):
        """Get the category part of the name."""
        tname = ""
        if name.startswith("_"):
            tname = name[1:]
        else:
            tname = name

        i = tname.find(".")
        if i == -1:
            return tname
        else:
            return tname[:i]

    @staticmethod
    def attribute_part(name):
        """Get the attribute part of the name."""
        i = name.find(".")
        if i == -1:
            return None
        else:
            return name[i + 1:]


class ContainerBase:
    """Container base class for data and definition objects."""
    def __init__(self, name):
        # The enclosing scope of the data container (e.g. data_/save_)
        self.__name = name
        # List of category names within this container -
        self.__object_name_list = []
        # dictionary of DataCategory objects keyed by category name.
        self.__object_catalog = {}
        self.__type = None

    def get_type(self):
        """Get container type."""
        return self.__type

    def set_type(self, type_):
        """Set container type."""
        self.__type = type_

    @property
    def name(self):
        """Get container name."""
        return self.__name

    def set_name(self, name):
        """Set container name."""
        self.__name = name

    def exists(self, name):
        """Determine if object name exists in object catalog."""
        return (name in self.__object_catalog)

    def get_object(self, name):
        """Get object from object catalog."""
        if name in self.__object_catalog:
            return self.__object_catalog[name]
        else:
            return None

    def get_object_name_list(self):
        """Get list of object names."""
        return self.__object_name_list

    def append(self, obj):
        """Add the input object to the current object catalog.
        An existing object of the same name will be overwritten."""
        if obj.name is not None:
            if obj.name not in self.__object_catalog:
                self.__object_name_list.append(obj.name)
            self.__object_catalog[obj.name] = obj

    def replace(self, obj):
        """Replace an existing object with the input object."""
        if (obj.name is not None) and (
                obj.name in self.__object_catalog):
            self.__object_catalog[obj.name] = obj

    def print_it(self, file_=stdout, type_="brief"):
        """Dump information about container to specified file object."""
        file_.write(
            "+ %s container: %30s contains %4d categories\n" % (
                self.get_type(), self.name,
                len(self.__object_name_list)))
        for name in self.__object_name_list:
            file_.write("--------------------------------------------\n")
            file_.write("Data category: %s\n" % name)
            if type_ == 'brief':
                self.__object_catalog[name].print_it(file_)
            else:
                self.__object_catalog[name].dump_it(file_)

    def rename(self, current_name, new_name):
        """Change the name of an object in place."""
        try:
            i = self.__object_name_list.index(current_name)
            self.__object_name_list[i] = new_name
            self.__object_catalog[new_name] = self.__object_catalog[
                current_name]
            self.__object_catalog[new_name].set_name(new_name)
            return True
        except KeyError:
            return False

    def remove(self, current_name):
        """Revmove object by name.
        Return True on success or False otherwise."""
        try:
            if current_name in self.__object_catalog:
                del self.__object_catalog[current_name]
                i = self.__object_name_list.index(current_name)
                del self.__object_name_list[i]
                return True
            else:
                return False
        except KeyError:
            pass
        return False


class DefinitionContainer(ContainerBase):
    """Container for definitions."""

    def __init__(self, name):
        super(DefinitionContainer, self).__init__(name)
        self.set_type('definition')

    def is_category(self):
        """Determine if container contains category objects."""
        if self.exists('category'):
            return True
        return False

    def is_attribute(self):
        """Determine if container contains item objects."""
        if self.exists('item'):
            return True
        return False

    def print_it(self, fh=stdout, type_="brief"):
        """Print information about container to file object."""
        fh.write("Definition container: %30s contains %4d categories\n" %
                 (self.name, len(self.get_object_name_list())))
        if self.is_category():
            fh.write("Definition type: category\n")
        elif self.is_attribute():
            fh.write("Definition type: item\n")
        else:
            fh.write("Definition type: undefined\n")

        for name in self.get_object_name_list():
            fh.write("--------------------------------------------\n")
            fh.write("Definition category: %s\n" % name)
            if type_ == 'brief':
                self.get_object(name).print_it(fh)
            else:
                self.get_object(name).dumpId(fh)


class DataContainer(ContainerBase):
    """Container class for DataCategory objects."""

    def __init__(self, name):
        super(DataContainer, self).__init__(name)
        self.set_type('data')
        self.__global_flag = False
        self.__current_row = None

    def invoke_data_block_method(self, method):
        """Invoke a method for the given data block."""
        self.__current_row = 1
        # TODO - remove exec() commands!
        exec(method.get_inline())

    def set_global(self):
        """Set global flag to True."""
        self.__global_flag = True

    def get_global(self):
        """Return global flag."""
        return self.__global_flag


class DataCategoryBase:
    """Base object definition for a data category."""

    def __init__(self, name, attribute_name_list=None, row_list=None):
        self._name = name
        if row_list is not None:
            self._row_list = row_list
        else:
            self._row_list = []

        if attribute_name_list is not None:
            self._attribute_name_list = attribute_name_list
        else:
            self._attribute_name_list = []
        self._catalog = {}
        self._num_attributes = 0
        self.__setup()

    def __setup(self):
        self._num_attributes = len(self._attribute_name_list)
        self._catalog = {}
        for attribute_name in self._attribute_name_list:
            attribute_name_lower = attribute_name.lower()
            self._catalog[attribute_name_lower] = attribute_name

    def set_row_list(self, row_list):
        """Set row list."""
        self._row_list = row_list

    def set_attribute_name_list(self, attribute_name_list):
        """Set attribute name list."""
        self._attribute_name_list = attribute_name_list
        self.__setup()

    def set_name(self, name):
        """Set name."""
        self._name = name

    def get(self):
        """Set name, attribute name list, and row list."""
        return (self._name, self._attribute_name_list, self._row_list)


class DataCategory(DataCategoryBase):
    """Methods for creating, accessing, formatting PDBx cif data categories."""

    def __init__(self, name, attribute_name_list=None, row_list=None):
        super().__init__(name, attribute_name_list, row_list)
        self.__lfh = stdout
        self.__current_row_index = 0
        self.__current_attribute = None
        self.__avoid_embedded_quoting = False
        self.__whitespace_re = re.compile(r"\s")
        self.__whitespace_quotes_re = re.compile(r"[\s'\"]")
        self.__newline_re = re.compile(r"[\n\r]")
        self.__single_quote_re = re.compile(r"[']")
        self.__whitespace_single_quote_re = re.compile(r"('\s)|(\s')")
        self.__double_quote_re = re.compile(r'["]')
        self.__whitespace_double_quote_re = re.compile(r'("\s)|(\s")')
        self.__integer_re = re.compile(r'^[0-9]+$')
        self.__float_re = re.compile(
            r'^-?(([0-9]+)[.]?|([0-9]*[.][0-9]+))([(][0-9]+[)])?([eE][+-]?[0-9]+)?$')
        self.__data_type_list = [
            'DT_NULL_VALUE', 'DT_INTEGER', 'DT_FLOAT', 'DT_UNQUOTED_STRING',
            'DT_ITEM_NAME', 'DT_DOUBLE_QUOTED_STRING',
            'DT_SINGLE_QUOTED_STRING', 'DT_MULTI_LINE_STRING',
        ]
        self.__format_type_list = [
            'FT_NULL_VALUE', 'FT_NUMBER', 'FT_NUMBER', 'FT_UNQUOTED_STRING',
            'FT_QUOTED_STRING', 'FT_QUOTED_STRING', 'FT_QUOTED_STRING',
            'FT_MULTI_LINE_STRING'
        ]

    def __getitem__(self, item):
        """Implements list-type functionality.

        Implements op[x] for some special cases:
            item = integer - returns the row in category (normal list behavior)
            item = string - returns the value of attribute 'x' in first row
        """
        if isinstance(item, int):
            return self._row_list[item]

        elif isinstance(item, str):
            try:
                self.get_attribute_index(item)
                return self._row_list[0][item]
            except (IndexError, KeyError):
                raise KeyError
        raise TypeError(item)

    @property
    def current_attribute(self):
        """Get current attribute."""
        return self.__current_attribute

    @property
    def current_row_index(self):
        """Get current row index."""
        return self.__current_row_index

    @property
    def row_list(self):
        """Get list of rows."""
        return self._row_list

    @property
    def row_count(self):
        """Get number of rows."""
        return len(self._row_list)

    def get_row(self, index):
        """Get specified row.
        Returns empty array if row not found."""
        try:
            return self._row_list[index]
        except IndexError:
            return []

    def remove_row(self, index):
        """Remove specified row."""
        try:
            if ((index >= 0) and (index < len(self._row_list))):
                del self._row_list[index]
                if self.__current_row_index >= len(self._row_list):
                    self.__current_row_index = len(self._row_list) - 1
                return True
            else:
                pass
        except IndexError:
            pass
        return False

    def get_full_row(self, index):
        """Return a full row based on the length of the the attribute list."""
        try:
            if len(self._row_list[index]) < self._num_attributes:
                self._row_list[index] += ['?'] * (
                    self._num_attributes - len(self._row_list[index]))
            return self._row_list[index]
        except IndexError:
            return ['?'] * len(self._num_attributes)

    @property
    def name(self):
        """Get container name."""
        return self._name

    @property
    def attribute_list(self):
        """Get list of attributes."""
        return self._attribute_name_list

    @property
    def attribute_count(self):
        """Get number of attributes."""
        return len(self._attribute_name_list)

    @property
    def attribute_list_with_order(self):
        """Get list of attributes in order."""
        ordered_list = []
        for i, att in enumerate(self._attribute_name_list):
            ordered_list.append((att, i))
        return ordered_list

    def get_attribute_index(self, attribute_name):
        """Get index of given attribute.
        Raises IndexError."""
        return self._attribute_name_list.index(attribute_name)

    def has_attribute(self, attribute_name):
        """Indicate whether container has attribute."""
        return attribute_name in self._attribute_name_list

    @property
    def item_name_list(self):
        """List of attribute names as fully qualified item names."""
        item_name_list_ = []
        for att in self._attribute_name_list:
            item_name_list_.append("_" + self._name + "." + att)
        return item_name_list_

    def append(self, row):
        """Add row to container."""
        self._row_list.append(row)

    def append_attribute(self, attribute_name):
        """Add attribute to container."""
        attribute_name_lower = attribute_name.lower()
        if attribute_name_lower in self._catalog:
            index = self._attribute_name_list.index(
                self._catalog[attribute_name_lower])
            self._attribute_name_list[index] = attribute_name
            self._catalog[attribute_name_lower] = attribute_name
        else:
            self._attribute_name_list.append(attribute_name)
            self._catalog[attribute_name_lower] = attribute_name
        self._num_attributes = len(self._attribute_name_list)

    def append_attribute_extend_rows(self, attribute_name):
        """Append attribute and extend rows."""
        attribute_name_lower = attribute_name.lower()
        if attribute_name_lower in self._catalog:
            index = self._attribute_name_list.index(
                self._catalog[attribute_name_lower])
            self._attribute_name_list[index] = attribute_name
            self._catalog[attribute_name_lower] = attribute_name
            self.__lfh.write(
                "Appending existing attribute %s\n" % attribute_name)
        else:
            self._attribute_name_list.append(attribute_name)
            self._catalog[attribute_name_lower] = attribute_name
            # add a placeholder to any existing rows for the new attribute.
            if len(self._row_list) > 0:
                for row in self._row_list:
                    row.append("?")
        self._num_attributes = len(self._attribute_name_list)

    def get_value(self, attribute_name=None, row_index=None):
        """Get value for specified attribute and row."""
        if attribute_name is None:
            attribute = self.__current_attribute
        else:
            attribute = attribute_name
        if row_index is None:
            index = self.__current_row_index
        else:
            index = row_index
        if isinstance(attribute, str) and isinstance(index, int):
            return self._row_list[index][
                self._attribute_name_list.index(attribute)]
        raise IndexError(attribute)

    def set_value(self, value, attribute_name=None, row_index=None):
        """Set value of attribute."""
        if attribute_name is None:
            attribute = self.__current_attribute
        else:
            attribute = attribute_name
        if row_index is None:
            index = self.__current_row_index
        else:
            index = row_index
        if isinstance(attribute, str) and isinstance(index, int):
            try:
                # if row index is out of range - add the rows
                for _ in range(index + 1 - len(self._row_list)):
                    self._row_list.append(self.__empty_row)
                row_len = len(self._row_list[index])
                ind = self._attribute_name_list.index(attribute)
                # extend the list if needed
                if ind >= row_len:
                    self._row_list[index].extend(
                        [None for _ in range(2 * ind - row_len)])
                self._row_list[index][ind] = value
            except IndexError:
                self.__lfh.write(
                    "DataCategory(setvalue) index error category"
                    " %s attribute %s index %d value %r\n" %
                    (self._name, attribute, index, value))
                traceback.print_exc(file=self.__lfh)
            except ValueError:
                self.__lfh.write(
                    "DataCategory(setvalue) value error category"
                    " %s attribute %s index %d value %r\n" %
                    (self._name, attribute, index, value))
                traceback.print_exc(file=self.__lfh)

    @property
    def __empty_row(self):
        """Return an empty row."""
        return [None for _ in range(len(self._attribute_name_list))]

    def replace_value(self, old_value, new_value, attribute_name):
        """Replace the value of the specified attribute."""
        num_replace = 0
        if attribute_name not in self._attribute_name_list:
            return num_replace
        ind = self._attribute_name_list.index(attribute_name)
        for row in self._row_list:
            if row[ind] == old_value:
                row[ind] = new_value
                num_replace += 1
        return num_replace

    def replace_substring(self, old_value, new_value, attribute_name):
        """Replace substring of value of given attribute.
        Return Boolean flag indicating success."""
        replace_ok = False
        if attribute_name not in self._attribute_name_list:
            return replace_ok
        ind = self._attribute_name_list.index(attribute_name)
        for row in self._row_list:
            val = row[ind]
            row[ind] = val.replace(old_value, new_value)
            if val != row[ind]:
                replace_ok = True
        return replace_ok

    def invoke_attribute_method(self, attribute_name, method):
        """Invoke method of current attribute."""
        self.__current_row_index = 0
        self.__current_attribute = attribute_name
        self.append_attribute(attribute_name)
        ind = self._attribute_name_list.index(attribute_name)
        if len(self._row_list) == 0:
            row = [None] * len(self._attribute_name_list)*2
            row[ind] = None
            self._row_list.append(row)
        for row in self._row_list:
            row_len = len(row)
            if ind >= row_len:
                row.extend([None] * (2 * ind - row_len))
                row[ind] = None
            # TODO - just say "no" to exec()
            exec(method.get_inline())
            self.__current_row_index += 1

    def invoke_category_method(self, method):
        """Invoke method of current category."""
        self.__current_row_index = 0
        # TODO - remove exec()
        exec(method.get_inline())

    @property
    def max_attribute_list_length(self):
        """Get maximum attribute list length."""
        max_list = [0] * len(self._attribute_name_list)
        for row in self._row_list:
            for index, value in enumerate(row):
                max_list[index] = max(max_list[index], len(value))
        return max_list

    def rename_attribute(self, current_attribute_name, new_attribute_name):
        """Change the name of an attribute in place."""
        try:
            i = self._attribute_name_list.index(current_attribute_name)
            self._attribute_name_list[i] = new_attribute_name
            del self._catalog[current_attribute_name.lower()]
            self._catalog[new_attribute_name.lower()] = new_attribute_name
            return True
        except KeyError:
            return False

    def print_it(self, file_=stdout):
        """Print container information."""
        file_.write("--------------------------------------------\n")
        file_.write(
            " Category: %s attribute list length: %d\n" %
            (self._name, len(self._attribute_name_list)))
        for attr in self._attribute_name_list:
            file_.write(" Category: %s attribute: %s\n" % (self._name, attr))

        file_.write(" Row value list length: %d\n" % len(self._row_list))
        for row in self._row_list[:2]:
            if len(row) == len(self._attribute_name_list):
                for index, value in enumerate(row):
                    file_.write(" %30s: %s ...\n" % (
                        self._attribute_name_list[index], str(value)[:30]))
            else:
                file_.write(
                    "+WARNING - %s data length %d attribute name length %s "
                    "mismatched\n" % (
                        self._name, len(row),
                        len(self._attribute_name_list)))

    def dump_it(self, file_=stdout):
        """Dump contents of container."""
        file_.write("--------------------------------------------\n")
        file_.write(
            " Category: %s attribute list length: %d\n" %
            (self._name, len(self._attribute_name_list)))
        for attr in self._attribute_name_list:
            file_.write(" Category: %s attribute: %s\n" % (self._name, attr))

        file_.write(" Value list length: %d\n" % len(self._row_list))
        for row in self._row_list:
            for index, value in enumerate(row):
                file_.write(" %30s: %s\n" % (
                    self._attribute_name_list[index], value))

    def __format_pdbx(self, inp):
        """Format input data following PDBx quoting rules."""
        try:
            if inp is None:
                return ("?", 'DT_NULL_VALUE')
            # pure numerical values are returned as unquoted strings
            if (isinstance(inp, int) or self.__integer_re.search(str(inp))):
                return ([str(inp)], 'DT_INTEGER')
            if (isinstance(inp, float) or self.__float_re.search(str(inp))):
                return ([str(inp)], 'DT_FLOAT')
            # null value handling
            if inp in (".", "?"):
                return ([inp], 'DT_NULL_VALUE')
            if inp == "":
                return (["."], 'DT_NULL_VALUE')
            # Contains white space or quotes ?
            if not self.__whitespace_quotes_re.search(inp):
                if inp.startswith("_"):
                    return (self.__double_quoted_list(inp), 'DT_ITEM_NAME')
                else:
                    return ([str(inp)], 'DT_UNQUOTED_STRING')
            else:
                if self.__newline_re.search(inp):
                    return (
                        self.__semicolon_quoted_list(inp),
                        'DT_MULTI_LINE_STRING')
                else:
                    if self.__avoid_embedded_quoting:
                        # change priority to choose double quoting where possible.
                        if (
                                not self.__double_quote_re.search(inp) and not
                                self.__whitespace_single_quote_re.search(inp)):
                            return (
                                self.__double_quoted_list(inp),
                                'DT_DOUBLE_QUOTED_STRING')
                        elif (
                                not self.__single_quote_re.search(inp) and not
                                self.__whitespace_double_quote_re.search(inp)):
                            return (
                                self.__single_quoted_list(inp),
                                'DT_SINGLE_QUOTED_STRING')
                        else:
                            return (
                                self.__semicolon_quoted_list(inp),
                                'DT_MULTI_LINE_STRING')
                    else:
                        # change priority to choose double quoting where possible.
                        if not self.__double_quote_re.search(inp):
                            return (
                                self.__double_quoted_list(inp),
                                'DT_DOUBLE_QUOTED_STRING')
                        elif not self.__single_quote_re.search(inp):
                            return (
                                self.__single_quoted_list(inp),
                                'DT_SINGLE_QUOTED_STRING')
                        else:
                            return (
                                self.__semicolon_quoted_list(inp),
                                'DT_MULTI_LINE_STRING')
        except ValueError:
            traceback.print_exc(file=self.__lfh)

    def __data_type_pdbx(self, inp):
        """Detect the PDBx data type."""
        if inp is None:
            return 'DT_NULL_VALUE'
        # pure numerical values are returned as unquoted strings
        if isinstance(inp, int) or self.__integer_re.search(str(inp)):
            return 'DT_INTEGER'
        if isinstance(inp, float) or self.__float_re.search(str(inp)):
            return 'DT_FLOAT'
        # null value handling
        if inp in (".", "?"):
            return 'DT_NULL_VALUE'
        if inp == "":
            return 'DT_NULL_VALUE'
        # Contains white space or quotes ?
        if not self.__whitespace_quotes_re.search(inp):
            if inp.startswith("_"):
                return 'DT_ITEM_NAME'
            else:
                return 'DT_UNQUOTED_STRING'
        else:
            if self.__newline_re.search(inp):
                return 'DT_MULTI_LINE_STRING'
            else:
                if self.__avoid_embedded_quoting:
                    if (
                            not self.__single_quote_re.search(inp) and not
                            self.__whitespace_double_quote_re.search(inp)):
                        return 'DT_DOUBLE_QUOTED_STRING'
                    elif (
                            not self.__double_quote_re.search(inp) and not
                            self.__whitespace_single_quote_re.search(inp)):
                        return 'DT_SINGLE_QUOTED_STRING'
                    else:
                        return 'DT_MULTI_LINE_STRING'
                else:
                    if not self.__single_quote_re.search(inp):
                        return 'DT_DOUBLE_QUOTED_STRING'
                    elif not self.__double_quote_re.search(inp):
                        return 'DT_SINGLE_QUOTED_STRING'
                    else:
                        return 'DT_MULTI_LINE_STRING'

    @staticmethod
    def __single_quoted_list(inp):
        """Generate a single-quoted list from the input."""
        return ["'"] + [inp] + ["'"]

    @staticmethod
    def __double_quoted_list(inp):
        """Generate a double-quoted list from the input."""
        return ['"'] + [inp] + ['"']

    @staticmethod
    def __semicolon_quoted_list(inp):
        """Generate a semicolon-delimited quoted list from the input."""
        if inp[-1] == '\n':
            return ["\n", ";"] + [inp] + [";", "\n"]
        else:
            return ["\n", ";"] + [inp] + ["\n", ";", "\n"]

    def get_value_formatted(self, attribute_name=None, row_index=None):
        """Get formatted version of value."""
        if attribute_name is None:
            attribute = self.__current_attribute
        else:
            attribute = attribute_name
        if row_index is None:
            index = self.__current_row_index
        else:
            index = row_index
        if isinstance(attribute, str) and isinstance(index, int):
            try:
                list_, _ = self.__format_pdbx(
                    self._row_list[index][
                        self._attribute_name_list.index(attribute)])
                return "".join(list_)
            except IndexError:
                self.__lfh.write(
                    "attribute_name %s index %r rowdata %r\n" %
                    (attribute_name, index, self._row_list[index]))
                raise IndexError
        raise TypeError(attribute)

    def get_value_formatted_by_index(self, attribute_index, row_index):
        """Get value formatted by index."""
        list_, _ = self.__format_pdbx(
            self._row_list[row_index][attribute_index])
        return "".join(list_)

    def get_max_attribute_list_length(self, steps=1):
        """Get maximum length of attribute value list."""
        max_list = [0] * len(self._attribute_name_list)
        for _ in self._row_list[::steps]:
            for index, value in enumerate(self._attribute_name_list):
                max_list[index] = max(max_list[index], len(str(value)))
        return max_list

    def get_format_type_list(self, steps=1):
        """Get a formatted type list."""
        try:
            current_data_type_list = ['DT_NULL_VALUE'] * len(
                self._attribute_name_list)
            for row in self._row_list[::steps]:
                for index, value in enumerate(self._attribute_name_list):
                    data_type = self.__data_type_pdbx(value)
                    data_index = self.__data_type_list.index(data_type)
                    current_type = current_data_type_list[index]
                    current_index = self.__data_type_list.index(
                        current_type)
                    current_index = max(current_index, data_index)
                    current_data_type_list[index] = self.__data_type_list[
                        current_index]
            # Map the format types to the data types
            current_format_type_list = []
            for data_type in current_data_type_list:
                index = self.__data_type_list.index(data_type)
                current_format_type_list.append(self.__format_type_list[index])
        except IndexError:
            self.__lfh.write(
                "PdbxDataCategory(get_format_type_list) ++Index error at "
                "index %d in row %r\n" %
                (index, row))
        return current_format_type_list, current_data_type_list

    @property
    def get_format_type_list_x(self):
        """Alternate version of format type list."""
        current_data_type_list = ['DT_NULL_VALUE'] * len(
            self._attribute_name_list)
        for _ in self._row_list:
            for index, value in enumerate(self._attribute_name_list):
                data_type = self.__data_type_pdbx(value)
                data_index = self.__data_type_list.index(data_type)
                current_type = current_data_type_list[index]
                current_index = self.__data_type_list.index(current_type)
                current_index = max(current_index, data_index)
                current_data_type_list[index] = self.__data_type_list[
                    current_index]
        # Map the format types to the data types
        current_format_type_list = []
        for data_type in current_data_type_list:
            index = self.__data_type_list.index(data_type)
            current_format_type_list.append(self.__format_type_list[index])
        return current_format_type_list, current_data_type_list
