##
# File: PdbxReader.py
# Date: 2012-01-09 Jdw Adapted from PdbxParser
#
# Updates:
#
# 2012-01-09 - (jdw) Separate reader and writer classes.
#
# 2012-09-02 - (jdw) Revise tokenizer to better handle embedded quoting.
#
##
"""PDBx/mmCIF dictionary and data file parser.

.. note::

   Acknowledgements:

   The tokenizer used in this module is modeled after the clever parser
   design used in the PyMMLIB package.

   PyMMLib Development Group:

   Authors: Ethan Merritt: merritt@u.washington.edu, Jay Painter: jay.painter@gmail.com

   See: http://pymmlib.sourceforge.net/
"""
import re
from .containers import DataCategory, DefinitionContainer, DataContainer
from .errors import PdbxSyntaxError


class PdbxReader:
    """PDBx reader for data files and dictionaries."""

    def __init__(self, input_file):
        """Initialize.

        :param file input_file: input file handle; e.g. as returned by open().
        """
        self.__current_line_number = 0
        self.__input_file = input_file
        self.__state_dict = {
            "data": "ST_DATA_CONTAINER",
            "loop": "ST_TABLE",
            "global": "ST_GLOBAL_CONTAINER",
            "save": "ST_DEFINITION",
            "stop": "ST_STOP",
        }

    def read(self, container_list):
        """Appends to the input list of definition and data containers.

        :param list container_list:  list of :class:`~pdbx.containers.ContainerBase` containers to append to.
        """
        self.__current_line_number = 0
        try:
            self.__parser(self.__tokenizer(self.__input_file), container_list)
        except StopIteration:
            self.__syntax_error("Unexpected end of file")

    def __syntax_error(self, error_text):
        """Raise a PdbxSyntaxError.

        :param str error_text:  text for exception message
        :raises pdbx.errors.PdbxSyntaxError:  exception with error text
        """
        raise PdbxSyntaxError(self.__current_line_number, error_text)

    @staticmethod
    def __get_container_name(in_word) -> str:
        """Returns the name of the data_ or save_ container.

        :param str in_word:  input word
        """
        return str(in_word[5:]).strip()

    def __get_state(self, in_word) -> tuple:
        """Identifies reserved syntax elements and assigns an associated state.

        :param str in_word:  input word
        :returns: (reserved word, state) where:

          * reserved word - is one of CIF syntax elements: data_, loop_,
          global_, save_, stop_

          * state - the parser state required to process this next section.
        """
        i = in_word.find("_")
        if i == -1:
            return None, "ST_UNKNOWN"
        try:
            reserved_word = in_word[:i].lower()
            return reserved_word, self.__state_dict[reserved_word]
        except KeyError:
            return None, "ST_UNKNOWN"

    def __parser(self, tokenizer, container_list):
        """Parser for PDBx data files and dictionaries.

        :param tokenizer: reentrant method recognizing data item names
          (_category.attribute), quoted strings (single, double and
          multi-line semi-colon delimited), and unquoted strings.
        :param list container_list: list-type container for data and
          definition objects parsed from from the input file.
          container_list is appended with data and definition objects.
        """
        # Working container - data or definition
        current_container = None
        # Working category container
        category_index = {}
        current_category = None
        current_row = None
        state = None

        # Find the first reserved word and begin capturing data.
        for (
            current_category_name,
            current_attribute_name,
            current_quoted_string,
            current_word,
        ) in tokenizer:
            if current_word is None:
                continue
            reserved_word, state = self.__get_state(current_word)
            if reserved_word is not None:
                break
        else:
            # empty file
            return

        while True:
            # Set the current state: at this point in the processing cycle we
            # are expecting a token containing # either a '_category.attribute'
            # or a reserved word.
            if current_category_name is not None:
                state = "ST_KEY_VALUE_PAIR"
            elif current_word is not None:
                reserved_word, state = self.__get_state(current_word)
            else:
                self.__syntax_error("Miscellaneous syntax error")
                return

            # Process _category.attribute value assignments
            if state == "ST_KEY_VALUE_PAIR":
                try:
                    current_category = category_index[current_category_name]
                except KeyError:
                    # A new category is encountered - create a container and
                    # add a row
                    category_index[current_category_name] = DataCategory(
                        current_category_name
                    )
                    current_category = category_index[current_category_name]
                    try:
                        current_container.append(current_category)
                    except AttributeError:
                        self.__syntax_error(
                            "Category cannot be added to data_ block"
                        )
                        return
                    current_row = []
                    current_category.append(current_row)
                else:
                    # Recover the existing row from the category
                    try:
                        current_row = current_category[0]
                    except IndexError:
                        self.__syntax_error(
                            "Internal index error accessing category data"
                        )
                        return
                # Check for duplicate attributes and add attribute to table.
                if current_attribute_name in current_category.attribute_list:
                    self.__syntax_error(
                        "Duplicate attribute encountered in category"
                    )
                    return
                else:
                    current_category.append_attribute(current_attribute_name)
                # Get the data for this attribute from the next token
                tok_category, _, current_quoted_string, current_word = next(
                    tokenizer
                )
                if tok_category is not None or (
                    current_quoted_string is None and current_word is None
                ):
                    self.__syntax_error(
                        "Missing data for item _%s.%s"
                        % (current_category_name, current_attribute_name)
                    )
                if current_word == "?":
                    current_row.append(None)
                elif current_word == ".":
                    current_row.append("")
                elif current_word is not None:
                    # Validation check token for misplaced reserved words
                    reserved_word, state = self.__get_state(current_word)
                    if reserved_word is not None:
                        self.__syntax_error(
                            "Unexpected reserved word: %s" % (reserved_word)
                        )
                    current_row.append(current_word)
                elif current_quoted_string is not None:
                    current_row.append(current_quoted_string)
                else:
                    self.__syntax_error("Missing value in item-value pair")
                try:
                    (
                        current_category_name,
                        current_attribute_name,
                        current_quoted_string,
                        current_word,
                    ) = next(tokenizer)
                except StopIteration:
                    return
                continue

            # Process a loop_ declaration and associated data
            if state == "ST_TABLE":
                # The category name in the next current_category_name,
                # current_attribute_name pair defines the name of the category
                # container.
                (
                    current_category_name,
                    current_attribute_name,
                    current_quoted_string,
                    current_word,
                ) = next(tokenizer)
                if (current_category_name is None) or (
                    current_attribute_name is None
                ):
                    self.__syntax_error(
                        "Unexpected token in loop_ declaration"
                    )
                    return
                # Check for a previous category declaration.
                if current_category_name in category_index:
                    self.__syntax_error(
                        "Duplicate category declaration in loop_"
                    )
                    return
                current_category = DataCategory(current_category_name)
                try:
                    current_container.append(current_category)
                except AttributeError:
                    self.__syntax_error(
                        "loop_ declaration outside of data_ block or save_ "
                        "frame"
                    )
                    return
                current_category.append_attribute(current_attribute_name)
                # Read the rest of the loop_ declaration
                for (
                    current_category_name,
                    current_attribute_name,
                    current_quoted_string,
                    current_word,
                ) in tokenizer:
                    if current_category_name is None:
                        break
                    if current_category_name != current_category.name:
                        self.__syntax_error(
                            "Changed category name in loop_ declaration"
                        )
                        return
                    current_category.append_attribute(current_attribute_name)
                else:
                    # formal CIF 1.1 grammar expects at least one value
                    self.__syntax_error("loop_ without values")
                # If the next token is a 'word', check it for any reserved
                # words
                if current_word is not None:
                    reserved_word, state = self.__get_state(current_word)
                    if reserved_word is not None:
                        if reserved_word == "stop":
                            return
                        else:
                            self.__syntax_error(
                                "Unexpected reserved word after loop "
                                "declaration: %s" % (reserved_word)
                            )
                # Read the table of data for this loop_
                while True:
                    current_row = []
                    current_category.append(current_row)
                    for _ in current_category.attribute_list:
                        if current_word == "?":
                            current_row.append(None)
                        elif current_word == ".":
                            current_row.append("")
                        elif current_word is not None:
                            current_row.append(current_word)
                        elif current_quoted_string is not None:
                            current_row.append(current_quoted_string)
                        try:
                            (
                                current_category_name,
                                current_attribute_name,
                                current_quoted_string,
                                current_word,
                            ) = next(tokenizer)
                        except StopIteration:
                            return
                    # loop_ data processing ends if a new _category.attribute
                    # is encountered
                    if current_category_name is not None:
                        break
                    # A reserved word is encountered
                    if current_word is not None:
                        reserved_word, state = self.__get_state(current_word)
                        if reserved_word is not None:
                            break
                continue

            if state == "ST_DEFINITION":
                # Ignore trailing unnamed saveframe delimiters e.g. 'save_'
                state_name = self.__get_container_name(current_word)
                if state_name:
                    current_container = DefinitionContainer(state_name)
                    container_list.append(current_container)
                    category_index = {}
                    current_category = None
            elif state == "ST_DATA_CONTAINER":
                data_name = self.__get_container_name(current_word)
                if not data_name:
                    data_name = "unidentified"
                current_container = DataContainer(data_name)
                container_list.append(current_container)
                category_index = {}
                current_category = None
            elif state == "ST_STOP":
                return
            elif state == "ST_GLOBAL":
                current_container = DataContainer("blank-global")
                current_container.set_global()
                container_list.append(current_container)
                category_index = {}
                current_category = None
            elif state == "ST_UNKNOWN":
                self.__syntax_error(
                    "Unrecognized syntax element: " + str(current_word)
                )
                return
            else:
                assert False, f"unhandled state {state}"

            try:
                (
                    current_category_name,
                    current_attribute_name,
                    current_quoted_string,
                    current_word,
                ) = next(tokenizer)
            except StopIteration:
                return

    def __tokenizer(self, input_file):
        """Tokenizer method for the mmCIF syntax file.

        Each return/yield from this method returns information about the next
        token in the form of a tuple with the following structure:
            (category name, attribute name, quoted strings, words w/o quotes
            or white space)
        Differentiated the regular expression to the better handle embedded
        quotes.

        :param file input_file:  file object ready for reading
        :rtype: Iterator[tuple]
        """
        # Regex definition for mmCIF syntax - semi-colon delimited strings are
        # handled outside of this regex.
        mmcif_re = re.compile(
            r"(?:"
            r"(?:_(.+?)[.](\S+))"
            "|"  # _category.attribute
            r"(?:['](.*?)(?:[']\s|[']$))"
            "|"  # single quoted strings
            r"(?:[\"](.*?)(?:[\"]\s|[\"]$))"
            "|"  # double quoted strings
            r"(?:\s*#.*$)"
            "|"  # comments (dumped)
            r"(\S+)"  # unquoted words
            r")"
        )
        file_iterator = iter(input_file)
        # Tokenizer loop begins here
        for line in file_iterator:
            self.__current_line_number += 1
            # Dump comments
            if line.startswith("#"):
                continue
            # Gobble up the entire semi-colon/multi-line-delimited string and
            # and stuff this into the string slot in the return tuple
            if line.startswith(";"):
                multiline_string = [line[1:]]
                for line in file_iterator:
                    self.__current_line_number += 1
                    if line.startswith(";"):
                        break
                    multiline_string.append(line)
                else:
                    self.__syntax_error("unterminated multi-line string")
                # remove trailing new-line that is part of the \n; delimiter
                multiline_string[-1] = multiline_string[-1].rstrip()
                yield (None, None, "".join(multiline_string), None)
                # Need to process the remainder of the current line -
                line = line[1:]

            # Apply regex to the current line consolidate the single/double
            # quoted within the quoted string category
            for match in mmcif_re.finditer(line):
                match_groups = match.groups()
                if match_groups != (None, None, None, None, None):
                    if match_groups[2] is not None:
                        quoted_string = match_groups[2]
                    elif match_groups[3] is not None:
                        quoted_string = match_groups[3]
                    else:
                        quoted_string = None
                    groups = (
                        match_groups[0],
                        match_groups[1],
                        quoted_string,
                        match_groups[4],
                    )
                    yield groups

    def __tokenizer_org(self, input_file):
        """Tokenizer method for the mmCIF syntax file.

        Each return/yield from this method returns information about the next
        token in the form of a tuple with the following structure:
            (category name, attribute name, quoted strings, words w/o quotes
            or white space)

        :param file input_file:  file object ready for reading
        :rtype: Iterator[tuple]
        """
        # Regex definition for mmCIF syntax - semi-colon delimited strings are
        # handled outside of this regex.
        mmcif_re = re.compile(
            r"(?:"
            r"(?:_(.+?)[.](\S+))"
            "|"  # _category.attribute
            r"(?:['\"](.*?)(?:['\"]\s|['\"]$))"
            "|"  # quoted strings
            r"(?:\s*#.*$)"
            "|"  # comments (dumped)
            r"(\S+)"  # unquoted words
            r")"
        )
        file_iterator = iter(input_file)
        # Tokenizer loop begins here
        while True:
            line = next(file_iterator)
            self.__current_line_number += 1
            # Dump comments
            if line.startswith("#"):
                continue
            # Gobble up the entire semi-colon/multi-line delimited string and
            # and stuff this into the string slot in the return tuple
            if line.startswith(";"):
                multiline_string = [line[1:]]
                while True:
                    line = next(file_iterator)
                    self.__current_line_number += 1
                    if line.startswith(";"):
                        break
                    multiline_string.append(line)
                # remove trailing new-line that is part of the \n; delimiter
                multiline_string[-1] = multiline_string[-1].rstrip()
                yield (None, None, "".join(multiline_string), None)
                # Need to process the remainder of the current line
                line = line[1:]
            # Apply regex to the current line
            for match in mmcif_re.finditer(line):
                groups = match.groups()
                if groups != (None, None, None, None):
                    yield groups
