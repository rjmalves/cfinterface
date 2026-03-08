Performance Tips
================

``cfinterface`` v1.9.0 includes several internal optimizations that improve
performance in file reading and writing scenarios. Beyond these automatic
improvements, there are usage patterns that allow developers to extract even
more performance when modeling files with the framework.

This page describes the internal optimizations and guides how to take advantage
of them through conscious design choices.

Regex Cache in Adapters
------------------------

In previous versions, each read call that used a regular expression pattern
recompiled the pattern from the original string. Starting from v1.9.0, the
adapter module maintains a global dictionary ``_pattern_cache`` that stores the
compiled objects for each pattern after its first use.

The impact is transparent to the user: the same pattern passed in
``BEGIN_PATTERN`` or ``END_PATTERN`` of a
:class:`~cfinterface.components.block.Block` is compiled only once, no matter
how many times the file is read during program execution.

No additional action is required; the cache is automatic. The only consideration
is to keep patterns as stable literal strings in the class definition, avoiding
the construction of dynamic patterns at runtime, which would generate distinct
cache entries and negate the benefit.

.. code-block:: python

    from cfinterface.components.block import Block

    class MyBlock(Block):
        # Pattern compiled once and reused across all reads
        BEGIN_PATTERN = r"^BEGIN"
        END_PATTERN = r"^END"

FloatField Optimization
-------------------------

The ``_textual_write()`` method of
:class:`~cfinterface.components.floatfield.FloatField` was rewritten to perform
at most three formatting attempts, regardless of the value of
``decimal_digits``. The previous implementation iterated through a loop of size
O(decimal_digits) to find the number of decimal places that fits in the field.

To get the most out of this optimization, declare ``size`` and
``decimal_digits`` with the minimum values needed to represent the values in
your domain. Oversized fields still work correctly, but fields sized to the
actual value eliminate unnecessary formatting attempts.

.. code-block:: python

    from cfinterface.components.floatfield import FloatField
    from cfinterface.components.line import Line

    # Prefer size adjusted to the domain of the value
    price_field = FloatField(size=10, starting_position=0, decimal_digits=2)

    # Avoid unnecessarily large fields
    # price_field = FloatField(size=30, starting_position=0, decimal_digits=15)

    line = Line([price_field])

Array-Based Containers
-----------------------

The container classes
:class:`~cfinterface.data.registerdata.RegisterData`,
``BlockData``, and ``SectionData`` have been migrated from linked-list
structures to Python lists (``list``) with an auxiliary index by type.

The main practical consequences are:

- ``len()`` is now O(1) instead of O(n) as in the previous implementation
- Iteration over all elements remains O(n), but with better memory locality
  (contiguous elements in memory)
- The ``previous`` and ``next`` properties of records, blocks, and sections are
  now computed from the position in the container, with no additional storage cost

This gain is automatic for any code that uses the existing file classes without
modification.

Batch Reading with read_many()
--------------------------------

When multiple files of the same type need to be read, the loop pattern with
individual instantiation can be replaced by the class method
:meth:`~cfinterface.files.registerfile.RegisterFile.read_many`, available on
:class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile`, and
:class:`~cfinterface.files.sectionfile.SectionFile`.

.. code-block:: python

    # Before: individual reading in a loop
    from my_module import MyFile

    files = []
    for path in paths:
        f = MyFile.read(path)
        files.append(f)

.. code-block:: python

    # After: batch reading with read_many()
    from my_module import MyFile

    # Returns a dict[str, MyFile] keyed by path
    files = MyFile.read_many(paths)

    # Access by path
    file = files["/path/to/file.txt"]

The ``read_many()`` method accepts the optional ``version`` parameter to
select the versioning schema, in the same way as ``read()``:

.. code-block:: python

    files = MyFile.read_many(paths, version="1.0")

Column Selection in TabularParser
------------------------------------

The :class:`~cfinterface.components.tabular.TabularParser` parses positional
(or delimited) text lines and converts each declared column into a list of
values. In large tabular files, declaring only the necessary columns reduces
the type conversion work for each line read.

Use :class:`~cfinterface.components.tabular.ColumnDef` to list only the
columns of interest, omitting the rest:

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField
    from cfinterface.components.integerfield import IntegerField

    # File has 5 columns; only 2 are needed
    required_columns = [
        ColumnDef(name="code", field=LiteralField(size=8, starting_position=0)),
        ColumnDef(name="value", field=FloatField(size=12, starting_position=20, decimal_digits=4)),
        # Columns at positions 8-19 and 32+ are simply ignored
    ]

    parser = TabularParser(required_columns)
    data = parser.parse_lines(lines)
    # {"code": [...], "value": [...]}

For tabular sections integrated with the framework, declare only the necessary
columns in the ``COLUMNS`` class attribute of your
:class:`~cfinterface.components.tabular.TabularSection` subclass:

.. code-block:: python

    from cfinterface.components.tabular import TabularSection, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    class DataSection(TabularSection):
        COLUMNS = [
            ColumnDef(name="id", field=LiteralField(size=8, starting_position=0)),
            ColumnDef(name="result", field=FloatField(size=12, starting_position=20, decimal_digits=3)),
        ]
        HEADER_LINES = 1
        END_PATTERN = r"^---"

General Tips
-------------

The following tips complement the internal optimizations described above and
apply to any code that uses ``cfinterface``.

**Reuse file class instances for multiple reads**

The ``read()`` method is a class method that returns a new instance on each
call. When the same file needs to be read again (for example, after a write),
prefer saving and reusing the existing instance or use ``read_many()`` for a
known set of paths at once.

**Use the StorageType enum instead of literal strings**

The ``STORAGE`` attribute accepts both strings (``"TEXT"``, ``"BINARY"``) and
the enum :class:`~cfinterface.storage.StorageType`. The use of strings has been
deprecated since v1.9.0 and emits a warning at runtime. Always prefer the enum:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MyFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = StorageType.TEXT  # correct
        # STORAGE = "TEXT"  # deprecated; avoid

**Declare ENCODING as a single string when the encoding is known**

The ``ENCODING`` attribute accepts a single string or a list of strings. When
passed as a list, the framework tries each encoding in order until a read
succeeds. If the file encoding is known and fixed, declare ``ENCODING`` as a
string directly to eliminate the unnecessary attempts:

.. code-block:: python

    class MyFile(RegisterFile):
        REGISTERS = [MyRecord]
        ENCODING = "latin-1"           # direct read, no extra attempts
        # ENCODING = ["latin-1", "utf-8"]  # only needed when the
        #                                   # encoding may vary
