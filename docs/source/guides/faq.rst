Frequently Asked Questions (FAQ)
=================================

This page collects the most common questions about using ``cfinterface``,
organized by topic. For complete details on each class and method,
see the API reference in the *Module Reference* section and the
:doc:`architecture overview </guides/architecture>`.

When should I use Register, Block, or Section?
------------------------------------------------

The choice depends on the structure of the file you need to model:

- **Register** -- use when each relevant line in the file is identified
  by a fixed prefix (e.g., ``"NR"``, ``"DA"``). The
  :class:`~cfinterface.components.register.Register` compares the beginning of each
  line against the ``IDENTIFIER`` attribute to decide which record type to
  process. Use :class:`~cfinterface.files.registerfile.RegisterFile` as the
  file class.

- **Block** -- use when the relevant data lies between a start line and an
  end line identifiable by regular expressions (e.g.,
  ``BEGIN_PATTERN = r"^SECTION"`` and ``END_PATTERN = r"^END"``). The
  :class:`~cfinterface.components.block.Block` delegates to the developer the
  implementation of ``read()`` and ``write()``. Use
  :class:`~cfinterface.files.blockfile.BlockFile` as the file class.

- **Section** -- use when the file is divided into ordered, sequential
  blocks without begin and end delimiters. Each section is processed in
  the order in which it appears in the file class's ``SECTIONS`` list. Use
  :class:`~cfinterface.files.sectionfile.SectionFile` as the file class.

In summary:

+------------------------+-------------------------------------------+
| Model                  | When to use                               |
+========================+===========================================+
| ``RegisterFile``       | Lines with a fixed prefix identifier      |
+------------------------+-------------------------------------------+
| ``BlockFile``          | Blocks with begin and end delimiters      |
+------------------------+-------------------------------------------+
| ``SectionFile``        | Ordered sections without delimiters       |
+------------------------+-------------------------------------------+

How do I handle binary files?
-------------------------------

Set ``STORAGE = StorageType.BINARY`` in your file class. The framework
will open the file in binary mode and delegate the reading and writing of
each field to the ``_binary_read`` and ``_binary_write`` methods of the
declared fields.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MyBinaryFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = StorageType.BINARY
        ENCODING = "utf-8"

    file = MyBinaryFile.read("/path/to/file.bin")

The native fields (:class:`~cfinterface.components.floatfield.FloatField` and
:class:`~cfinterface.components.integerfield.IntegerField`) already implement
``_binary_read`` and ``_binary_write`` using ``numpy`` internally. For custom
fields, you must implement these methods when subclassing
:class:`~cfinterface.components.field.Field`.

.. note::

   Never use the literal string ``"BINARY"`` for the ``STORAGE`` attribute. This
   usage has been deprecated since version 1.9.0. Always use
   ``StorageType.BINARY``.

How do I use the pandas integration?
--------------------------------------

Pandas support is an optional dependency. Install it with:

.. code-block:: bash

    pip install cfinterface[pandas]

Then use the ``_as_df()`` method available on
:class:`~cfinterface.files.registerfile.RegisterFile` to obtain a
:class:`pandas.DataFrame` with all records of a given type:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile

    class MyFile(RegisterFile):
        REGISTERS = [RecordA, RecordB]

    file = MyFile.read("/path/to/file.txt")

    # Returns a DataFrame with all instances of RecordA
    df = file._as_df(RecordA)
    print(df.head())

The method performs a lazy import (only when called), so the rest of the
code works normally even without pandas installed. The import only fails at
the moment ``_as_df()`` is invoked without the package present.

For tabular data within sections, the
:class:`~cfinterface.components.tabular.TabularParser` provides the static
method :meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`:

.. code-block:: python

    from cfinterface.components.tabular import TabularParser

    data = parser.parse_lines(lines)
    df = TabularParser.to_dataframe(data)

How do I define a custom field?
---------------------------------

Subclass :class:`~cfinterface.components.field.Field` and implement the
four abstract methods. The methods ``_textual_read`` and ``_textual_write``
handle text mode; ``_binary_read`` and ``_binary_write`` handle binary mode.

.. code-block:: python

    from cfinterface.components.field import Field

    class BooleanField(Field):
        """Field that represents a boolean as 'S'/'N' in text
        or 0x01/0x00 in binary."""

        def _textual_read(self, line: str) -> bool:
            token = line[self._starting_position:self._ending_position].strip()
            return token == "S"

        def _textual_write(self) -> str:
            return ("S" if self._value else "N").ljust(self._size)

        def _binary_read(self, line: bytes) -> bool:
            return line[self._starting_position:self._ending_position] == b"\x01"

        def _binary_write(self) -> bytes:
            return b"\x01" if self._value else b"\x00"

The field can be used in any :class:`~cfinterface.components.line.Line`
in the same way as native fields:

.. code-block:: python

    from cfinterface.components.line import Line

    line = Line([BooleanField(size=1, starting_position=0)])
    value = line.read("S")  # True

Note that ``_textual_write`` and ``_binary_write`` receive no arguments
besides ``self``: the value to be written is read from ``self._value``.

How do I resolve common parsing errors?
-----------------------------------------

**A field value returns ``None``**

The field could not interpret the content of the line. Check that
``starting_position`` and ``size`` are correct for the actual file. The method
:meth:`~cfinterface.components.field.Field.read` catches ``ValueError`` and
returns ``None`` when the conversion fails.

**Encoding error (``UnicodeDecodeError``)**

The file uses an encoding different from those listed in ``ENCODING``. Adjust
the file class's ``ENCODING`` attribute to include the correct encoding:

.. code-block:: python

    class MyFile(RegisterFile):
        REGISTERS = [...]
        ENCODING = ["latin-1", "utf-8"]  # tries latin-1 first

The framework tries each encoding from the list in order and uses the first one
that does not raise an error.

**Record not found in the file**

Check that ``IDENTIFIER`` and ``IDENTIFIER_DIGITS`` exactly match the prefix in
the file. ``IDENTIFIER_DIGITS`` must equal the number of characters (or bytes,
in binary mode) that form the identifier. An incorrect value causes the method
:meth:`~cfinterface.components.register.Register.matches` to never return
``True``.

.. code-block:: python

    from cfinterface.components.register import Register
    from cfinterface.components.line import Line
    from cfinterface.components.literalfield import LiteralField

    class NameRecord(Register):
        IDENTIFIER = "NM"       # exactly 2 characters
        IDENTIFIER_DIGITS = 2   # must match len(IDENTIFIER)
        LINE = Line([LiteralField(size=20, starting_position=2)])

How do I use TabularParser?
-----------------------------

:class:`~cfinterface.components.tabular.TabularParser` converts lists of
text lines into a dictionary of lists indexed by column name, and also
provides the inverse operation.

The column schema is declared with
:class:`~cfinterface.components.tabular.ColumnDef`. Each ``ColumnDef`` requires
its own field instance -- fields are mutated in-place during reading and cannot
be shared between columns.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    columns = [
        ColumnDef(name="product", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="price", field=FloatField(size=10, starting_position=20, decimal_digits=2)),
    ]
    parser = TabularParser(columns)

    lines = [
        "Product A               12.50     ",
        "Product B                7.99     ",
    ]
    data = parser.parse_lines(lines)
    # {"product": ["Product A", "Product B"], "price": [12.5, 7.99]}

For integration with ``SectionFile``, use
:class:`~cfinterface.components.tabular.TabularSection` and declare only the
class attributes ``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN``, and
``DELIMITER``. See the complete example in the gallery:
:ref:`sphx_glr_examples_plot_tabular_parsing.py`.

How does file versioning work?
--------------------------------

Versioning allows the same file class to read content produced by different
versions of the schema, without needing separate classes.

Declare the class attribute ``VERSIONS`` as a dictionary mapping version keys
(strings compared lexicographically) to lists of component types:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class VersionedFile(RegisterFile):
        REGISTERS = [RecordV2A, RecordV2B]  # default schema (most recent)
        VERSIONS = {
            "1.0": [RecordV1A],
            "2.0": [RecordV2A, RecordV2B],
        }
        STORAGE = StorageType.TEXT

    # Selects the schema of the most recent version <= "1.5", i.e., "1.0"
    file = VersionedFile.read("/path/to/file.txt", version="1.5")

    # Validates whether the read content matches the expected schema
    result = file.validate(version="1.0")
    print(result.matched)       # True if all expected types were found
    print(result.missing_types) # expected types that did not appear in the file

The function :func:`~cfinterface.versioning.resolve_version` performs the
lexicographic resolution: given ``version="1.5"`` and keys ``["1.0", "2.0"]``,
it returns the components for ``"1.0"`` (the largest key less than or equal to ``"1.5"``).

For complete versioning examples, see the gallery example:
:ref:`sphx_glr_examples_plot_versioned_file.py`.
