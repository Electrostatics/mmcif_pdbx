"""Error classes for PDBx/mmCIF."""


class PdbxError(Exception):
    """Class for general errors."""


class PdbxSyntaxError(Exception):
    """Class for syntax errors."""

    def __init__(self, line_number, text):
        super().__init__(self)
        self.line_number = line_number
        self.text = text

    def __str__(self):
        return "%%ERROR - [at line: %d] %s" % (self.line_number, self.text)
