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
   I have some raw text for describing my content, because I was mean for being irectly read by someone.

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
            date_field = DatetimeField(size=7, starting_position=0, format="%y/%m")
            index_field = IntegerField(size=4, starting_position=11)
            value_field = FloatField(size=6, starting_position=19)
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
            block_dfs = [b.data for b in self.data.get_blocks_of_type(FirstBlock)]
            return pd.concat(block_dfs, ignore_index=True)

    file = MyBlockFile.read("/path/to/file_describe_above.txt")
    assert type(file.first_block_data) == pd.DataFrame
    file.write("/path/to/some_other_desired_file.txt")
    # The content of the written file should be the same
    # as the source file


As one can see, the `read` and `write` methods are implemented in a generic way in the base `BlockFile` class, and will deal with any of the block types informed in the `BLOCKS` class attribute. However, each :ref:`Block <block>` must implement its own `read` and `write` methods, which will be called when the `BlockFile` class successfully matches one of the BEGIN_PATTERN expressions. All the blocks that were successully read will be stored in the `data` field, accessible inside the built `file` object. This is a :ref:`BlockData <blockdata>` object, which implements a double linked list of blocks that were parsed from the given file.

The developer may edit any of the desired blocks or any of its fields. When calling the `write` function, all blocks will be written to the file, following the login of its own `write` function, implemented by the developer.

Any content in the file that was not matched as being in any of the given blocks is stored as an instance of the :ref:`DefaultBlock <defaultblock>` object, which is an one-line block for reproducing the entire file contents when writing it back.

Registers and RegisterFiles
---------------------------

A special case of blocks in a file is when the length of each block is exactly 1. In this case, each block is a single line, and defining all the requirements of the :ref:`Block <block>` + :ref:`BlockFile <blockfile>` approach can be a little too much.

For handling this special case, the developer can use another approach, which is defined by :ref:`RegisterFile <registerfile>` abstraction, together with the :ref:`Register <register>` components.

Suppose there is a file with the following content

.. code-block:: none
   :linenos:

   DATA_HIGH  ID001   sudo.user  10/20/2025  901.25
   DATA_HIGH  ID002   sudo.user  10/21/2025  100.20
   DATA_HIGH  ID003   test.user  10/30/2025  100.20

   DATA_LOW   01/01/2024   105.23
   DATA_LOW   01/02/2024    29.15
   DATA_LOW   01/03/2024     5.05

In this case, each line is defined by an unique beginning pattern in its first columns, together with a set of fields that are positioned on different places depending on the beginning pattern. 

Each pattern determines a different :ref:`Register <register>` class to be built, and the entire file can have a variable number of objects for each register.

One possible approach for modeling the file using the :ref:`RegisterFile <registerfile>` abstraction is:


.. code-block:: python
   :linenos:

    from typing import Union, Optional, List
    from datetime import datetime
    import pandas as pd

    from cfinterface import IntegerField, FloatField, DatetimeField, LiteralField
    from cfinterface import Line, Register, RegisterFile

    class DataHigh(Register):
        IDENTIFIER = "DATA_HIGH"
        IDENTIFIER_DIGITS = 9
        LINE = Line(
            [
                LiteralField(size=6, starting_position=11),
                LiteralField(size=9, starting_position=19),
                DatetimeField(size=10, starting_position=30, format="%M/$d/%Y"),
                FloatField(size=6, starting_position=42, decimal_digits=2),
            ]
        )

        @property
        def field_id(self) -> str:
            """
            Identifier of the DataHigh element.
            """
            return self.fdata[0]

        @field_id.setter
        def field_id(self, v: str):
            self.data[0] = v

        @property
        def user(self) -> str:
            """
            User associated with the DataHigh element.
            """
            return self.fdata[1]

        @user.setter
        def user(self, v: str):
            self.data[1] = v

        @property
        def date(self) -> datetime:
            """
            Date associated with the DataHigh element.
            """
            return self.data[2]

        @date.setter
        def date(self, v: datetime):
            self.data[2] = v

        @property
        def value(self) -> float:
            """
            Value associated with the DataHigh element.
            """
            return self.data[3]

        @value.setter
        def value(self, v: float):
            self.data[3] = v


    class DataLow(Register):
        IDENTIFIER = "DATA_LOW"
        IDENTIFIER_DIGITS = 8
        LINE = Line(
            [
                DatetimeField(size=10, starting_position=11, format="%M/$d/%Y"),
                FloatField(size=6, starting_position=24, decimal_digits=2),
            ]
        )

        
        @property
        def date(self) -> datetime:
            """
            Date associated with the DataLow element.
            """
            return self.data[0]

        @date.setter
        def date(self, v: datetime):
            self.data[0] = v

        @property
        def value(self) -> float:
            """
            Value associated with the DataLow element.
            """
            return self.data[1]

        @value.setter
        def value(self, v: float):
            self.data[1] = v


    class MyRegisterFile(RegisterFile):

        REGISTERS = [
            DataHigh,
            DataLow,
        ]

        # All the reading and writing logic is done by the framework,
        # finding which register is in each line and calling their implemetations.
        # The user can implement some properties for better suiting its use cases:

        @property
        def data_high(self) -> Optional[Union[DataHigh, List[DataHigh]]]:
            return self.data.get_registers_of_type(DataHigh)

        @property
        def data_low(self) -> Optional[Union[DataLow, List[DataLow]]]:
            return self.data.get_registers_of_type(DataLow)

    file = MyRegisterFile.read("/path/to/file_describe_above.txt")
    assert len(file.data_high) == 3
    assert file.data_high[0].field_id == "ID001"
    file.write("/path/to/some_other_desired_file.txt")
    # The content of the written file should be the same
    # as the source file

As one can see, the `read` and `write` methods are implemented in a generic way in the base `RegisterFile` class, and will deal with any of the register types informed in the `REGISTER` class attribute. All the registers that were successully read will be stored in the `data` field, accessible inside the built `file` object. This is a :ref:`RegisterData <registerdata>` object, which implements a double linked list of registers that were parsed from the given file.

The developer may edit any of the desired registers or any of its fields. When calling the `write` function, all registers will be written to the file, following the formatting of each of field.

Any content in the file that was not matched as being in any of the given registers is stored as an instance of the :ref:`DefaultRegister <defaultregister>` object, which is an one-field register for reproducing the entire file contents when writing it back.


Sections and SectionFiles
-------------------------

Another special case of blocks in a file is when the beginning pattern of each block does not matter. In this case, the file to be modeled is usually well determined in terms of content and ordering. However, if the developer also models others files using the :ref:`BlockFile <blockfile>` and :ref:`RegisterFile <registerfile>` approaches and wants to maintain all the files in the same framework, the :ref:`Section <section>` and :ref:`SectionFile <sectionfile>` can be used. Also, following the framework allows versioning each file part separately, which can be useful for schemas that change over time.


Suppose there is a file with the following content

.. code-block:: none
   :linenos:

   Date       Index     Value
   ----------------------------
   2020/01        1    1000.0
   2020/02        1    2000.0
   2020/01        2    3000.0
   2020/02        2    4000.0
   2020/01        3    5000.0
   2020/02        3    6000.0
   ----------------------------

     Username    Last Login
   -------------------------
        admin    1996/01/01
     sunshine    2000/01/01
    pineapple    1996/01/01
        admin    1996/01/01
   -------------------------

If the file is such that always these two tables will be exhibited, in the same order, and there is no chance of repeating these information blocks, the :ref:`SectionFile <sectionfile>` approach can be used. Also, one may note that there is no such clear beginning and ending patterns like the previous :ref:`BlockFile <blockfile>` example.

One possible approach for modeling the file using the :ref:`SectionFile <sectionfile>` abstraction is:


.. code-block:: python
   :linenos:

    from typing import Union, Optional, List
    from datetime import datetime
    import pandas as pd

    from cfinterface import IntegerField, FloatField, DatetimeField, LiteralField
    from cfinterface import Line, Section, SectionFile

    class FirstSection(Section):

        __slots__ = [
            "__line_model",
        ]

        HEADER_LINE = "Date       Index     Value"
        MARGIN_LINE = "----------------------------"

        def __init__(self, previous=None, next=None, data=None) -> None:
            super().__init__(previous, next, data)
            date_field = DatetimeField(size=7, starting_position=0, format="%y/%m")
            index_field = IntegerField(size=4, starting_position=11)
            value_field = FloatField(size=6, starting_position=19)
            self.__line_model = Line([date_field, index_field, value_field])

        def __eq__(self, o: object) -> bool:
            if not isinstance(o, FirstSection):
                return False
            block: FirstSection = o
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

            # Discards the line with the header and margin
            for _ in range(2):
                file.readline()
            
            # Reads the data content
            dates = []
            indices = []
            values = []
            
            while True:

                line = file.readline()
                if self.MARGIN_LINE in line:
                    self.data = pd.DataFrame({"Date": dates, "Index": indices, "Value": values)
                    break

                date, index, value = self.__line_model.read()
                dates.append(date)
                indices.append(index)
                values.append(value)
    
        # Override
        def write(self, file: IO, *args, **kwargs):

            file.write(self.HEADER_LINE + "\n")
            file.write(self.MARGIN_LINE + "\n")

            # Writes data lines
            for _, line in self.data.iterrows():
                self.__line_model.write([line["Date"], line["Index"], line["Value"]])
            
            file.write(self.MARGIN_LINE + "\n")


    class SecondSection(Section):
        # Implement in a similar way for the second section specifics
    

    class MySectionFile(SectionFile):

        SECTIONS = [
            FirstSection,
            SecondSection,
        ]

        # All the reading and writing logic is done by the framework.
        # The user can implement some properties for better suiting its use cases:

        @property
        def first_section_data(self) -> pd.DataFrame:
            s = self.data.get_sections_of_type(FirstSection)
            return s.data

    file = MySectionFile.read("/path/to/file_described_above.txt")
    assert type(file.first_section_data) == pd.DataFrame
    file.write("/path/to/some_other_desired_file.txt")
    # The content of the written file should be the same
    # as the source file

As one can see, the `read` and `write` methods are implemented in a generic way in the base `SectionFile` class, and will call the specific section functions in the same order that they were declared in the `SECTION` class attribute. All the sections that were successully read will be stored in the `data` field, accessible inside the built `file` object. This is a :ref:`SectionData <sectiondata>` object, which implements a double linked list of sections  that were parsed from the given file. 

The developer may edit any of the desired sections or any of its fields. When calling the `write` function, all sections will be written to the file, following the formatting of each of field.

All data that may exist in the file after the last modeled section will be read as :ref:`DefaultSection <defaultsection>` objects. These are one-line sections used for compatibility with data not explicitly modeled by the developer.


File Encodings
---------------

Currently, when modeling a file through any of the aforementioned approaches, the developer can choose the preferred encoding for reading and writing. Also, instead of a single encoding, a list of encodings can be supplied, which will be used for reading an writing.

Some ways for specifying encodings are:

.. code-block:: python
   :linenos:

    from typing import IO
    import pandas as pd

    from cfinterface import BlockFile

    class MyBlockFileWithSingleEncoding(BlockFile):

        ENCODING = "utf-8"
    

    class MyBlockFileWithManyEncodings(BlockFile):

        ENCODING = ["utf-8", "latin-1", "ascii"]

When reading, each of the supplied encodings will be used, in order. The first encoding to successfully parse the whole file will end the reading process. For writing, the file model will always use the first encoding of the list.


Modeling Binary Files
----------------------

When a file contains data encoded in binary format instead of textual, the `cfinterface` framework is still applied for modeling its contents, supporting reading and writing. The same file models can be used, but with some differences in the meaning of some fundamental actions, which are better illustrated in the :ref:`examples page <examples>`.

For defining a file model as binary, one may set the class attribute:


.. code-block:: python
   :linenos:

    from typing import IO
    import pandas as pd

    from cfinterface import BlockFile

    class MyTextualFile(BlockFile):

        STORAGE = "TEXT"
    
    class MyBinaryFile(BlockFile):

        STORAGE = "BINARY"
    

Versioning Files
-----------------

Files can change their schema with time, resulting in multiple versions. One approach is to define multiple file models, but this could result in large amounts of copied and pasted code, since the changes in the schemas could be minimal.

The `cfinterface` supports file versioning by allowing the user to define the lists of elements (:ref:`Blocks <blocks>`, :ref:`Registers <registers>` or :ref:`Sections <sections>`) that exist on each version of the file.

For an example, suppose there is a file that was versioned. The file always contained two blocks, but one of them had a small change on its schema when the file version evolved from version `1.0` to `2.0`. In this case, the developer might do:


.. code-block:: python
   :linenos:

    from typing import IO
    import pandas as pd

    from cfinterface import Block, BlockFile

    class MyConstantBlock(Block):
        pass
    
    class MyVersionedOldBlock(Block):
        pass

    class MyVersionedNewBlock(Block):
        pass

    class MyVersionedFile(BlockFile):

        VERSIONS = {
            "1.0": [
                MyConstantBlock,
                MyVersionedOldBlock
            ],
            "2.0": [
                MyConstantBlock,
                MyVersionedNewBlock
            ]
        }


    MyVersionedFile.set_version("1.0")
    old_file = MyVersionedFile.read("path/to/old/file")
    MyVersionedFile.set_version("2.0")
    new_file = MyVersionedFile.read("path/to/new/file")


In this case, the default behavior for any file is reading on its latest version. If the user desires to read a previous version of the file, one can use the `set_version` class method for changing its behavior. The version comparison in done by Python native  `str` comparison.

If one chooses to set a version `V`, which is a non-existent key in the `VERSIONS` dict, the framework looks for the first version `W` among the dict keys such that `W <= V`. If no such key is found, the latest version is used. As an example in the previous code block, setting the `MyVersionedFile` version to `1.5` would fallback to `1.0`. However, setting it to `0.5` would result in using the latest `2.0` version.




