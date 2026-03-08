Migration Guide: v1.8.x to v1.9.0
====================================

cfinterface v1.9.0 is a feature release with some breaking changes for
downstream projects. This guide covers all changes that require modification of
existing code -- dependency changes, API replacements, and deprecated behaviors
-- as well as the new optional features that users can adopt at their own pace.

Read each section and apply the corresponding changes to your project before
upgrading the dependency to ``cfinterface>=1.9.0``. The `Migration Checklist`_
at the end summarizes the steps in order.

pandas as an Optional Dependency
----------------------------------

**What changed:** pandas is no longer a mandatory dependency of cfinterface.
Starting with version 1.9.0, only ``numpy>=2.0.0`` is required at runtime.
pandas is installed only when the ``[pandas]`` extra is explicitly requested.

This change reduces the installation environment size for projects that do not
use :meth:`~cfinterface.files.registerfile.RegisterFile._as_df` or
:meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`.

Before (v1.8.x):

.. code-block:: python

    # pandas was automatically installed with cfinterface
    pip install cfinterface

After (v1.9.0):

.. code-block:: python

    # Install the [pandas] extra only if you need DataFrame integration
    pip install cfinterface[pandas]

If your project imports ``pandas`` directly from code that assumed cfinterface
installed it, add ``pandas`` as an explicit dependency of your project or
install the extra:

.. code-block:: python

    # Before: implicit import that worked because cfinterface brought in pandas
    import pandas as pd
    df = pd.DataFrame(file.data)

    # After: install cfinterface[pandas] or declare pandas as your own
    # project dependency
    import pandas as pd  # requires pip install cfinterface[pandas]
    df = pd.DataFrame(file.data)

StorageType Enum
-----------------

**What changed:** The class attribute ``STORAGE`` of file classes
(:class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile`,
:class:`~cfinterface.files.sectionfile.SectionFile`) must now use
:class:`~cfinterface.storage.StorageType` instead of literal strings.
Using the strings ``"TEXT"`` or ``"BINARY"`` emits a
:class:`DeprecationWarning` at runtime and will be removed in a future
version.

:class:`~cfinterface.storage.StorageType` inherits from ``str``, so
``StorageType.TEXT == "TEXT"`` is ``True``. Code that only *reads* the
``STORAGE`` value and compares it with strings continues to work without
changes.

Before (v1.8.x):

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile

    class MyFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = "TEXT"  # literal string -- deprecated

    class MyBinaryFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = "BINARY"  # literal string -- deprecated

After (v1.9.0):

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MyFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = StorageType.TEXT  # enum -- correct

    class MyBinaryFile(RegisterFile):
        REGISTERS = [MyRecord]
        STORAGE = StorageType.BINARY  # enum -- correct

Deprecation of set_version()
------------------------------

**What changed:** The class method ``set_version()`` is deprecated. It
mutated the class state permanently, which caused unexpected behavior in
applications that read different versions of the same file in sequence. The
``version=`` argument in the :meth:`read` method replaces this functionality
safely and without side effects.

Before (v1.8.x):

.. code-block:: python

    from my_project.files import MyVersionedFile

    # set_version() mutated the class permanently
    MyVersionedFile.set_version("1.0")
    file_v1 = MyVersionedFile.read("data_v1.txt")

    MyVersionedFile.set_version("2.0")
    file_v2 = MyVersionedFile.read("data_v2.txt")

After (v1.9.0):

.. code-block:: python

    from my_project.files import MyVersionedFile

    # version= is passed directly to read(); the class is not mutated
    file_v1 = MyVersionedFile.read("data_v1.txt", version="1.0")
    file_v2 = MyVersionedFile.read("data_v2.txt", version="2.0")

The ``version=`` argument is supported by all three file types:
:meth:`~cfinterface.files.registerfile.RegisterFile.read`,
:meth:`~cfinterface.files.blockfile.BlockFile.read`, and
:meth:`~cfinterface.files.sectionfile.SectionFile.read`.

Array-Based Containers
-----------------------

**What changed:** The data container classes
(:class:`~cfinterface.data.registerdata.RegisterData`,
:class:`~cfinterface.data.blockdata.BlockData`,
:class:`~cfinterface.data.sectiondata.SectionData`) have been migrated from
linked-list structures to array-based containers (Python ``list``).
The main practical consequences are:

- **``len()`` is now O(1).** In previous versions, computing the collection
  size required traversing the pointer chain.
- **``previous`` and ``next`` are computed properties,** not stored attributes.
  The values are derived from the element's position in the internal array.
  The observable behavior is identical, but code that assigned directly to
  ``register.previous`` or ``register.next`` to reorganize elements will no
  longer work as expected -- use the container methods
  (:meth:`~cfinterface.data.registerdata.RegisterData.add_before`,
  :meth:`~cfinterface.data.registerdata.RegisterData.add_after`,
  :meth:`~cfinterface.data.registerdata.RegisterData.remove`) instead.
- **The primary access pattern remains the same.** Direct iteration and the
  method :meth:`~cfinterface.data.registerdata.RegisterData.of_type` continue
  to work without changes.

If your code relied on assigning ``previous``/``next`` as stored pointers,
refactor to use the container mutation methods:

.. code-block:: python

    # Before (v1.8.x): direct pointer manipulation
    new_record.next = existing_record
    new_record.previous = existing_record.previous
    # ... manual chaining ...

    # After (v1.9.0): use the container methods
    file.data.add_before(existing_record, new_record)

The typical read pattern remains identical:

.. code-block:: python

    # This pattern works the same in v1.8.x and v1.9.0
    for record in file.data.of_type(MyRecord):
        print(record.value)

New Features
-------------

The following features are additive and do not require changes to existing
code. Adopt them as needed by your project.

TabularParser and ColumnDef
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`cfinterface.components.tabular.TabularParser` provides a declarative
approach for parsing blocks of tabular content -- both fixed-width and
delimited. The column schema is declared as a list of
:class:`cfinterface.components.tabular.ColumnDef`.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    columns = [
        ColumnDef(name="name", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="value", field=FloatField(size=10, starting_position=20,
                                                 decimal_digits=2)),
    ]
    parser = TabularParser(columns)
    data = parser.parse_lines(["Product A               12.50     "])
    # {"name": ["Product A"], "value": [12.5]}

The class :class:`~cfinterface.components.tabular.TabularSection` simplifies
the integration of tabular blocks into ``SectionFile``.

read_many() -- Batch Reading
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`~cfinterface.files.registerfile.RegisterFile.read_many` reads multiple
files in a single call and returns a dictionary indexed by path:

.. code-block:: python

    files = MyFile.read_many(
        ["/data/jan.txt", "/data/feb.txt", "/data/mar.txt"]
    )
    # {"./data/jan.txt": <MyFile>, ...}

The ``version=`` argument is also accepted by ``read_many()``.

SchemaVersion and validate_version()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`cfinterface.versioning.SchemaVersion` and
:func:`cfinterface.versioning.validate_version` allow declaring schema versions
in a structured way and programmatically verifying whether the read content
matches the expected schema:

.. code-block:: python

    result = file.validate(version="2.0")
    if not result.matched:
        print("Missing types:", result.missing_types)

py.typed -- PEP 561
~~~~~~~~~~~~~~~~~~~~~

The ``py.typed`` marker has been added to the package, enabling downstream
type checking with mypy, pyright, and similar tools. No code changes are
required; the benefit is automatic upon upgrading to v1.9.0.

Migration Checklist
--------------------

Follow the steps below in order to migrate a project from v1.8.x to v1.9.0:

1. Update the dependency in your ``pyproject.toml`` or ``requirements.txt``
   to ``cfinterface>=1.9.0``.

2. If your project uses pandas (``_as_df()``, ``to_dataframe()``, or any
   indirect import via cfinterface), change the dependency to
   ``cfinterface[pandas]>=1.9.0`` or add ``pandas`` as an explicit dependency
   of your project.

3. Replace all occurrences of ``STORAGE = "TEXT"`` with
   ``STORAGE = StorageType.TEXT`` and ``STORAGE = "BINARY"`` with
   ``STORAGE = StorageType.BINARY`` in your file subclasses. Add the import
   ``from cfinterface.storage import StorageType`` to the affected files.

4. Replace all calls to ``set_version()`` with the ``version=`` argument in
   :meth:`read`. Example: ``MyClass.set_version("1.0"); MyClass.read(path)``
   becomes ``MyClass.read(path, version="1.0")``.

5. Check whether any code in your project directly assigns to the ``previous``
   or ``next`` attributes of records, blocks, or sections with the intent of
   reorganizing elements in the container. Replace those operations with the
   methods
   :meth:`~cfinterface.data.registerdata.RegisterData.add_before`,
   :meth:`~cfinterface.data.registerdata.RegisterData.add_after`, or
   :meth:`~cfinterface.data.registerdata.RegisterData.remove`.

6. Run your project's test suite to confirm compatibility. Pay attention to
   :class:`DeprecationWarning` entries in the logs -- they indicate deprecated
   patterns that still work but must be corrected before a future version.
