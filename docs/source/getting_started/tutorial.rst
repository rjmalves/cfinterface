Tutorial
=========

The `cinterface <https://github.com/rjmalves/cfinterface/>`_ framework is meant to be used when developing low-level interfaces to complex textual or binary files, where the explicit modeling of the file schema is a desired feature. The abstractions defined by the framework allow the user to divide the modeling of file schemas in meaningful pieces, enabling reuse of schemas and content while reading and writing files.

Three main file types are provided by the framework: :ref:`BlockFile <blockfile>`, :ref:`SectionFile <sectionfile>` and :ref:`RegisterFile <registerfile>`. Each of these file models are meant to use in specific situations.

:ref:`BlockFiles <blockfile>` are files which can be modeled as blocks of text (or bytes), which can be easily identified by a given beginning pattern and an optional ending pattern. These patterns can be given as regexes for the entity definition in the framework. The steps of reading a block are up to the user to define by overloading the `read` function.

:ref:`SectionFiles <sectionfile>` are a special case of BlockFiles that don't follow beginning or ending patterns, but can be divided in sections, which are direct divisions of the file content in a subset of lines or bytes. These are usually the simplest files, where the content does not vary in amount or contain repeating pieces.

:ref:`RegisterFiles <registerfile>` can be seen also as a special case of BlockFiles, where each block contain only one line. The actual implementation of the internals of a RegisterFile differ, however, from a BlockFile. Using the :ref:`Line <line>` entity from the framework, RegisterFiles are made in a way that many registers can be defined with little overhead from the developer, allowing to model an extensive set of patterns with little code maintenance.

Each of the files, together with some additional details on another abstractions provided by the framework, will be briefly shown in the following. For more details on each approach, check on the :ref:`examples <examples>` page. If your use case is not actually covered, please contribute with an `Issue <https://github.com/rjmalves/cfinterface/issues/new>`_.


Fields
------

The most fundamental components in the `cinterface <https://github.com/rjmalves/cfinterface/>`_ framework are the :ref:`Fields <fields>`. Being defined for both textual and binary interfaces, fields are containers for one specific data value, with a specific formatting, located in a file. The common base :ref:`Field <field>` class is used for defining generic reading and writing functions, which implementations are given by each specific subclass.

Each specific Field contain its own arguments. For instance, if the file being modeled contains a line in which a specific literal data is desired:

.. code-block:: none
   :linenos:

    |   Username (max. 30 chars)   | ...
    |   FooBar                     | ...

One can see that the `Username` begins in the second column and will contain at most 30 characters. So, one can define a :ref:`LiteralField <literalfield>` that will extract, format and store the content:

.. code-block:: python
   :linenos:

    from cfinterface import LiteralField

    username = LiteralField(size=30, starting_position=1)

    value = username.read("|   FooBar                     | ...")
    # The content "FooBar" can be accessed by both value and username.value
    assert value == "FooBar"
    assert username.value == "FooBar"

Other fields are used for storing numeric values, such as :ref:`IntegerField <integerfield>` and :ref:`FloatField <floatfield>`. The :ref:`DatetimeField <datetimefield>` is used specifically for constructing an `datetime <https://docs.python.org/3/library/datetime.html>`_ object directly from the file contents following one or more format strings.


Line
-----

Usually a line in a file contain more than just one piece of desired information. In this case, the :ref:`Field <field>` component is not enough for being able to model the given line for reading and writing. In these cases, the :ref:`Line <line>` component is the one suited for the task, being defined as a simple collection of fields. In the previous example, suppose that the actual file lines contain more than just the username:


.. code-block:: none
   :linenos:

    |   Username (max. 30 chars)   | Signup Date | Age | Balance ($) | ...
    |   FooBar                     |  2020-05-20 |  18 |       99.90 | ...

The line contents now are modeled by a list of fields, which define a :ref:`Line <line>`:

.. code-block:: python
   :linenos:

    from datetime import datetime

    from cfinterface import LiteralField, DatetimeField, IntegerField, FloatField, Line

    username = LiteralField(size=30, starting_position=1)
    signup_date = DatetimeField(size=13, starting_position=32, format="%Y-%m-%d")
    age = IntegerField(size=5, starting_position=46)
    balance = FloatField(size=13, starting_position=52, decimal_digits=2)

    line = Line(fields=[username, signup_date, age, balance])

    values = line.read("|   FooBar                     |  2020-05-20 |  18 |       99.90 | ...")
    assert values == ["FooBar", datetime(2020, 5, 20), 18, 99.90]



Blocks and BlockFiles
---------------------

Suppose there is a file which content resembles the following

.. code-block:: none
   :linenos:

    MY_FIRST_BLOCK_BEGINNING_PATTERN
    I have some raw text for describing my content, because I was mean for being directly read by someone.

    Now I have some data. After which I will be done.

    Date       Index     Value
    2020/01        1    1000.0
    2020/02        1    2000.0
    2020/01        2    3000.0
    2020/02        2    4000.0
    2020/01        3    5000.0
    2020/02        3    6000.0
    MY_FIRST_BLOCK_ENDING_PATTERN

    MY_SECOND_BLOCK_BEGINNING_PATTERN
    My content is completely different from the previous block...

      Username    Last Login
         admin    1996/01/01
      sunshine    2000/01/01
     pineapple    1996/01/01
         admin    1996/01/01
    MY_SECOND_BLOCK_ENDING_PATTERN

    MY_FIRST_BLOCK_BEGINNING_PATTERN
    ...
    MY_FIRST_BLOCK_ENDING_PATTERN

    MY_FIRST_BLOCK_BEGINNING_PATTERN
    ...
    MY_FIRST_BLOCK_ENDING_PATTERN

    MY_SECOND_BLOCK_BEGINNING_PATTERN
    ...
    MY_SECOND_BLOCK_ENDING_PATTERN

    ...


One may notice that the file is composed of two blocks of content that have clear beginning and ending patterns, but are written without an specific order in the file. Even the number of repetitions of both blocks cannot be discovered without parsing the whole file at least once. In this case, a :ref:`BlockFile <blockfile>` is the best approach for modeling it.

One possible approach for modeling the file using the :ref:`BlockFile <blockfile>` abstraction is:

.. code-block:: python
   :linenos:

    from typing import IO
    import pandas as pd

    from cfinterface import IntegerField, FloatField, DatetimeField, LiteralField
    from cfinterface import Line, Block, BlockFile

    class FirstBlock(Block):

        __slots__ = [
            "__header_lines",
            "__line_model",
        ]

        BEGIN_PATTERN = "MY_FIRST_BLOCK_BEGINNING_PATTERN"
        END_PATTERN = "MY_FIRST_BLOCK_ENDING_PATTERN"

        NUM_HEADER_LINES = 5

        def __init__(self, previous=None, next=None, data=None) -> None:
            super().__init__(previous, next, data)
            self.__header_lines = []
            date_field = DatetimeField()
            index_field = IntegerField()
            value_field = FloatField()
            self.__line_model = Line([date_field, index_field, value_field])

        def __eq__(self, o: object) -> bool:
            if not isinstance(o, FirstBlock):
                return False
            block: FirstBlock = o
            if not all(
                [
                    isinstance(self.data, pd.DataFrame),
                    isinstance(block.data, pd.DataFrame),
                ]
            ):
                return False
            else:
                return self.data.equals(block.data)

        # Override
        def read(self, file: IO, *args, **kwargs) -> bool:

            # Discards the line with the beginning pattern
            file.readline()

            # Reads header lines for writing later
            for _ in range(self.__class__.NUM_HEADER_LINES):
                self.__header_lines.append(file.readline())
            
            # Reads the data content
            dates = []
            indices = []
            values = []
            
            while True:

                line = file.readline()
                if FirstBlock.ends(line):
                    self.data = pd.DataFrame({"Date": dates, "Index": indices, "Value": values)
                    break

                date, index, value = self.__line_model.read()
                dates.append(date)
                indices.append(index)
                values.append(value)
    
        # Override
        def write(self, file: IO, *args, **kwargs):

            file.write(self.__class__.BEGIN_PATTERN + "\n")

            # Writes header lines
            for line in self.__header_lines:
                file.write(line)
            
            # Writes data lines
            for _, line in self.data.iterrows():
                self.__line_model.write([line["Date"], line["Index"], line["Value"]])
            
            file.write(self.__class__.END_PATTERN + "\n")


    class SecondBlock(Block):
        # Implement in a similar way for the second block specifics
    

    class MyBlockFile(BlockFile):

        BLOCKS = [
            FirstBlock,
            SecondBlock,
        ]

        # All the reading and writing logic is done by the framework,
        # finding when each block begins and calling their implemetations.
        # The user can implement some properties for better suiting its use cases:

        @property
        def first_block_data(self) -> pd.DataFrame:
            block_dfs = [b.data for b in self.data.of_type(FirstBlock)]
            return pd.concat(block_dfs, ignore_index=True)

    file = MyBlockFile.read("/path/to/file_describe_above.txt")
    assert type(file.first_block_data) == pd.DataFrame
    file.write("/path/to/some_other_desired_file.txt")
    # The content of the written file should be the same
    # as the source file


Sections and SectionFiles
-------------------------

TODO

Registers and RegisterFiles
---------------------------

TODO