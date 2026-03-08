Architecture Overview
=====================

``cfinterface`` is a declarative framework for building low-level interfaces with text or binary
files of complex structure. Instead of writing imperative code to iterate over file lines, the
developer declares the schema -- which fields exist, at which positions, how to identify each
record -- and the framework handles reading and writing. This approach makes the file schema
explicit, reusable, and independently testable.

The design follows a layered composition principle: atomic components are grouped into
intermediate components, which in turn are orchestrated by high-level file classes.
An adapter layer isolates the differences between textual and binary storage from the rest of
the code.

Component Hierarchy
--------------------

The full component hierarchy is illustrated below:

.. code-block:: text

    Field  (FloatField, IntegerField, LiteralField, DatetimeField)
      |
      v
    Line  (ordered sequence of Fields; delegates I/O to the adapter)
      |
      v
    Register / Block / Section  (intermediate components; operate on file handles)
      |
      v
    RegisterFile / BlockFile / SectionFile  (high-level file classes)

Each layer depends only on the layer immediately below it, keeping coupling minimal and
allowing each level to be tested and reused independently.

Fields
-------

:class:`cfinterface.components.field.Field` is the atomic unit of the framework. A ``Field``
represents a single positional value within a file line: it knows its starting position
(``starting_position``), its size in characters or bytes (``size``), and the current value
(``value``). The public methods :meth:`~cfinterface.components.field.Field.read` and
:meth:`~cfinterface.components.field.Field.write` accept both ``str`` and ``bytes``,
delegating internally to ``_textual_read``/``_binary_read`` or
``_textual_write``/``_binary_write``.

The framework provides four concrete subclasses ready for use:

:class:`cfinterface.components.floatfield.FloatField`
    Reads and writes floating-point numbers. Supports fixed notation (``format="F"``),
    scientific notation (``format="E"`` or ``format="D"``), and a configurable decimal
    separator. For binary storage uses ``numpy`` (``float16``, ``float32``, or ``float64``
    depending on ``size``).

:class:`cfinterface.components.integerfield.IntegerField`
    Reads and writes integers. In binary mode uses ``numpy`` (``int16``, ``int32``, or ``int64``).

:class:`cfinterface.components.literalfield.LiteralField`
    Reads and writes fixed-width strings, stripping whitespace from the edges when reading
    and left-aligning when writing.

:class:`cfinterface.components.datetimefield.DatetimeField`
    Reads and writes :class:`datetime.datetime` objects from one or more format strings.

Example -- defining a textual field:

.. code-block:: python

    from cfinterface import LiteralField, FloatField

    name = LiteralField(size=20, starting_position=0)
    balance = FloatField(size=12, starting_position=20, decimal_digits=2)

    line = "Current Account      -1234.56    "
    name.read(line)    # "Current Account"
    balance.read(line)   # -1234.56

Line
-----

:class:`cfinterface.components.line.Line` aggregates an ordered list of
:class:`~cfinterface.components.field.Field` instances and provides the methods
:meth:`~cfinterface.components.line.Line.read` and
:meth:`~cfinterface.components.line.Line.write` to operate on the entire line at once.
Internally, ``Line`` does not perform I/O directly: it instantiates a repository via the
function :func:`cfinterface.adapters.components.line.repository.factory`, passing the
configured ``StorageType``. That repository is what executes reading and writing according
to the storage backend (textual or binary).

``Line`` accepts an optional ``delimiter``: when provided, fields are separated by that
character instead of occupying fixed positions.

.. code-block:: python

    from cfinterface import LiteralField, FloatField
    from cfinterface.components.line import Line
    from cfinterface.storage import StorageType

    fields = [
        LiteralField(size=20, starting_position=0),
        FloatField(size=10, starting_position=20, decimal_digits=2),
    ]
    line = Line(fields, storage=StorageType.TEXT)
    values = line.read("Current Account     -1234.56  ")
    # values == ["Current Account", -1234.56]

Intermediate Components
------------------------

Intermediate components operate directly on file handles (``IO[Any]``) and implement the
logic for identifying and delimiting content blocks.

Register
~~~~~~~~~

:class:`cfinterface.components.register.Register` represents a single file line identified
by a fixed prefix. The class attribute ``IDENTIFIER`` defines the prefix (``str`` or
``bytes``) and ``IDENTIFIER_DIGITS`` specifies the number of characters or bytes that form
this identifier. The class attribute ``LINE`` is an instance of
:class:`~cfinterface.components.line.Line` that describes the fields after the identifier.

The class method :meth:`~cfinterface.components.register.Register.matches` checks whether a
line belongs to this record type by comparing its beginning with ``IDENTIFIER``.

.. code-block:: python

    from cfinterface.components.register import Register
    from cfinterface.components.line import Line
    from cfinterface.components.floatfield import FloatField

    class MonthlyValue(Register):
        IDENTIFIER = "VM"
        IDENTIFIER_DIGITS = 2
        LINE = Line([FloatField(size=10, starting_position=2, decimal_digits=2)])

Block
~~~~~~

:class:`cfinterface.components.block.Block` represents a block delimited by begin and end
patterns. The class attributes ``BEGIN_PATTERN`` and ``END_PATTERN`` are regular expressions
(``str`` or ``bytes``) that indicate where the block starts and ends. The attribute
``MAX_LINES`` (default: 10000) limits the number of lines processed per block as a safeguard
against infinite reads.

The class methods :meth:`~cfinterface.components.block.Block.begins` and
:meth:`~cfinterface.components.block.Block.ends` test a line against the corresponding
patterns. The methods :meth:`~cfinterface.components.block.Block.read` and
:meth:`~cfinterface.components.block.Block.write` must be implemented by the subclass.

.. code-block:: python

    from cfinterface.components.block import Block

    class DataSection(Block):
        BEGIN_PATTERN = r"^BEGIN"
        END_PATTERN = r"^END"

        def read(self, file, *args, **kwargs):
            # custom read logic
            return True

        def write(self, file, *args, **kwargs):
            # custom write logic
            return True

Section
~~~~~~~~

:class:`cfinterface.components.section.Section` represents an ordered, sequential division
of the file, without begin or end patterns. Sections are processed in the order in which they
appear in ``SectionFile.SECTIONS``. The class attribute ``STORAGE`` (of type
:class:`~cfinterface.storage.StorageType`) indicates whether the section operates in textual
or binary mode. The methods :meth:`~cfinterface.components.section.Section.read` and
:meth:`~cfinterface.components.section.Section.write` must be implemented by the subclass.

File Classes
-------------

File classes are the framework's entry point for the end user. Each one aggregates a set of
intermediate components and provides the high-level methods
:meth:`read`, :meth:`write`, :meth:`read_many`, and :meth:`validate`.

:class:`cfinterface.files.registerfile.RegisterFile`
    Models files composed of single-line records. The class attribute ``REGISTERS``
    is a list of :class:`~cfinterface.components.register.Register` subclasses in the order
    in which they may appear in the file.

:class:`cfinterface.files.blockfile.BlockFile`
    Models files composed of delimited blocks. The class attribute ``BLOCKS`` is a list
    of :class:`~cfinterface.components.block.Block` subclasses.

:class:`cfinterface.files.sectionfile.SectionFile`
    Models files composed of sequential sections. The class attribute ``SECTIONS`` is a
    list of :class:`~cfinterface.components.section.Section` subclasses.

Class attributes common to all file classes:

``STORAGE``
    :class:`~cfinterface.storage.StorageType` that indicates the storage backend
    (``StorageType.TEXT`` or ``StorageType.BINARY``). Default: ``StorageType.TEXT``.

``ENCODING``
    Text encoding to use (``str``) or list of encodings tried in order
    (``list[str]``). Default: ``["utf-8", "latin-1", "ascii"]``.

``VERSIONS``
    Optional dictionary mapping version keys to lists of component types,
    allowing the same file class to support multiple schema versions. See the
    `Versioning`_ section for details.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MyFile(RegisterFile):
        REGISTERS = [MonthlyValue]
        STORAGE = StorageType.TEXT
        ENCODING = "utf-8"

    file = MyFile.read("/path/to/file.txt")
    file.write("/path/to/output.txt")

Adapter Layer
--------------

The adapter layer isolates the differences between textual and binary storage from the rest
of the framework. The module :mod:`cfinterface.adapters.components.repository` defines the
hierarchy:

- :class:`~cfinterface.adapters.components.repository.Repository` -- abstract interface with
  static methods ``matches``, ``begins``, ``ends``, ``read``, and ``write``.
- :class:`~cfinterface.adapters.components.repository.TextualRepository` -- implementation for
  text files; uses ``file.readline()`` for reading and regex-based comparisons on strings.
- :class:`~cfinterface.adapters.components.repository.BinaryRepository` -- implementation for
  binary files; uses ``file.read(linesize)`` and byte comparisons.

The function :func:`cfinterface.adapters.components.repository.factory` receives a
:class:`~cfinterface.storage.StorageType` and returns the appropriate repository class.
When ``StorageType.TEXT`` is passed, it returns ``TextualRepository``; when
``StorageType.BINARY``, it returns ``BinaryRepository``. This factory pattern is the central
point that allows the framework to be agnostic to the storage type.

The regular expressions used by the adapters are compiled and cached on first use
(``_pattern_cache``), eliminating recompilation per call.

TabularParser
--------------

Introduced in version 1.9.0, :class:`cfinterface.components.tabular.TabularParser` provides
a declarative approach for parsing tabular content -- blocks of lines where each line
represents a data row with columns defined by fixed positions or by a delimiter.

The column schema is declared as a list of :class:`cfinterface.components.tabular.ColumnDef`,
a ``NamedTuple`` with two fields:

``name``
    Column name (key in the output dictionary).

``field``
    Instance of :class:`~cfinterface.components.field.Field` that defines the type, position,
    and size of the column. Each ``ColumnDef`` must use its own ``Field`` instance -- the
    ``Line.read()`` method mutates field values in-place, so sharing instances between columns
    produces incorrect results.

The main methods are:

:meth:`~cfinterface.components.tabular.TabularParser.parse_lines`
    Receives a list of strings and returns a dictionary whose keys are column names
    and whose values are lists of values read line by line.

:meth:`~cfinterface.components.tabular.TabularParser.format_rows`
    Inverse operation: receives a dictionary in the same format and returns a list of
    formatted strings.

:meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`
    Converts the dictionary returned by ``parse_lines`` into a ``pandas.DataFrame``. Requires
    the optional dependency ``cfinterface[pandas]``.

For integrated use with ``SectionFile``, the class
:class:`cfinterface.components.tabular.TabularSection` extends
:class:`~cfinterface.components.section.Section` and implements ``read()`` and ``write()``
automatically based on the class attributes ``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN``,
and ``DELIMITER``.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    columns = [
        ColumnDef(name="name", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="value", field=FloatField(size=10, starting_position=20, decimal_digits=2)),
    ]
    parser = TabularParser(columns)

    lines = [
        "Product A               12.50     ",
        "Product B                7.99     ",
    ]
    data = parser.parse_lines(lines)
    # data == {"name": ["Product A", "Product B"], "value": [12.5, 7.99]}

Versioning
-----------

The module :mod:`cfinterface.versioning` provides support for files whose schema evolves over
time, allowing the same file class to read content from different versions without needing
separate classes.

:class:`cfinterface.versioning.SchemaVersion`
    ``NamedTuple`` with three fields: ``key`` (version identifier as a string), ``components``
    (list of component types corresponding to this version), and ``description`` (optional text).

``VERSIONS``
    Class attribute of file classes (``RegisterFile``, ``BlockFile``, ``SectionFile``).
    It is a dictionary mapping version keys (strings compared lexicographically) to lists
    of component types. Example: ``{"1.0": [RegV1], "2.0": [RegV1, RegV2]}``.

:func:`cfinterface.versioning.resolve_version`
    Receives a requested version key and the ``VERSIONS`` dictionary. Returns the list of
    components whose key is the most recent available that is less than or equal to the
    requested version (lexicographic comparison). Returns ``None`` if the requested version
    is earlier than all available ones.

:func:`cfinterface.versioning.validate_version`
    Validates the read content against the expected component types. Returns a
    :class:`~cfinterface.versioning.VersionMatchResult` with the fields ``matched``,
    ``expected_types``, ``found_types``, ``missing_types``, ``unexpected_types``, and
    ``default_ratio``.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class VersionedFile(RegisterFile):
        REGISTERS = [MonthlyValueV2]
        VERSIONS = {
            "1.0": [MonthlyValueV1],
            "2.0": [MonthlyValueV2],
        }
        STORAGE = StorageType.TEXT

    # Reading while selecting a version without mutating the class
    file = VersionedFile.read("/path/to/file.txt", version="1.5")
    # resolve_version("1.5", VERSIONS) will return the components for "1.0"

    # Validating the read content
    result = file.validate(version="1.0")
    print(result.matched)  # True if the content matches the 1.0 schema

StorageType
------------

:class:`cfinterface.storage.StorageType` is an enumeration (``str``, ``Enum``) that replaces
the use of literal strings ``"TEXT"`` and ``"BINARY"`` to identify the storage backend.
It inherits from ``str``, which ensures backward compatibility: ``StorageType.TEXT == "TEXT"``
is ``True``.

The two available values are:

``StorageType.TEXT``
    Indicates textual storage. The file is opened in text mode and operations use
    ``str``.

``StorageType.BINARY``
    Indicates binary storage. The file is opened in binary mode and operations use
    ``bytes``.

The use of literal strings ``"TEXT"`` and ``"BINARY"`` in the ``STORAGE`` attribute of file
classes has been deprecated since version 1.9.0. The internal function ``_ensure_storage_type``
emits a :class:`DeprecationWarning` when a plain string is detected instead of an enumeration
member.

.. code-block:: python

    from cfinterface.storage import StorageType

    # Correct -- always use the enumeration
    class MyBinaryFile(RegisterFile):
        REGISTERS = [...]
        STORAGE = StorageType.BINARY

    # Deprecated -- do not use
    # STORAGE = "BINARY"

Extension Points
-----------------

``cfinterface`` is designed to be extended through subclassing. The main extension points for
downstream library developers are:

Field Subclasses
~~~~~~~~~~~~~~~~~

Create a subclass of :class:`~cfinterface.components.field.Field` to support data types not
covered by the native implementations. Implement the four abstract methods:
``_textual_read``, ``_binary_read``, ``_textual_write``, and ``_binary_write``.

.. code-block:: python

    from cfinterface.components.field import Field

    class BooleanField(Field):
        def _textual_read(self, line: str) -> bool:
            return line[self._starting_position:self._ending_position].strip() == "S"

        def _binary_read(self, line: bytes) -> bool:
            return line[self._starting_position:self._ending_position] == b"\x01"

        def _textual_write(self) -> str:
            return ("S" if self._value else "N").ljust(self._size)

        def _binary_write(self) -> bytes:
            return b"\x01" if self._value else b"\x00"

Register Subclasses
~~~~~~~~~~~~~~~~~~~~

Declare ``IDENTIFIER``, ``IDENTIFIER_DIGITS``, and ``LINE`` to define a new record type
identified by a prefix. No methods need to be overridden for the standard case of positional
reading and writing.

Block Subclasses
~~~~~~~~~~~~~~~~~

Declare ``BEGIN_PATTERN`` and ``END_PATTERN`` and implement ``read()`` and ``write()`` with
the processing logic specific to the block.

Section Subclasses
~~~~~~~~~~~~~~~~~~~

Declare ``STORAGE`` and implement ``read()`` and ``write()``. For tabular sections, prefer
subclassing :class:`~cfinterface.components.tabular.TabularSection` and declaring only
``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN``, and ``DELIMITER``.

VERSIONS Dictionaries
~~~~~~~~~~~~~~~~~~~~~~

Add the class attribute ``VERSIONS`` to any subclass of
:class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile`, or
:class:`~cfinterface.files.sectionfile.SectionFile` to enable schema selection by version at
read time, without needing to create separate subclasses for each version.

TabularParser with Custom Schemas
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instantiate :class:`~cfinterface.components.tabular.TabularParser` with a list of
:class:`~cfinterface.components.tabular.ColumnDef` instances to parse any tabular block,
whether fixed-width or delimited. The same instance can be reused for multiple files
with the same schema.
