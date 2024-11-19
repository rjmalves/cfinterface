Tutorial
=========

The `cinterface <https://github.com/rjmalves/cfinterface/>`_ framework is meant to be used when developing low-level interfaces to complex textual or binary files, where the explicit modeling of the file schema is a desired feature. The abstractions defined by the framework allow the user to divide the modeling of file schemas in meaningful pieces, enabling reuse of schemas and content while reading and writing files.

Three main file types are provided by the framework: :ref:`BlockFile <blockfile>`, :ref:`SectionFile <sectionfile>` and :ref:`RegisterFile <registerfile>`. Each of these file models are meant to use in specific situations.

:ref:`BlockFiles <blockfile>` are files which can be modeled as blocks of text (or bytes), which can be easily identified by a given beginning pattern and an optional ending pattern. These patterns can be given as regexes for the entity definition in the framework. The steps of reading a block are up to the user to define by overloading the `read` function.

:ref:`SectionFiles <sectionfile>` are a special case of BlockFiles that don't follow beginning or ending patterns, but can be divided in sections, which are direct divisions of the file content in a subset of lines or bytes. These are usually the simplest files, where the content does not vary in amount or contain repeating pieces.

:ref:`RegisterFiles <registerfile>` can be seen also as a special case of BlockFiles, where each block contain only one line. The actual implementation of the internals of a RegisterFile differ, however, from a BlockFile. Using the :ref:`Line <line>` entity from the framework, RegisterFiles are made in a way that many registers can be defined with little overhead from the developer, allowing to model an extensive set of patterns with little code maintenance.

Each of the files, together with some additional details on another abstractions provided by the framework, will be briefly shown in the following. For more details on each approach, check on the :ref:`examples <examples>` page. If your use case is not actually covered, please contribute with an `Issue <https://github.com/rjmalves/cfinterface/issues/new>`_.


BlockFile
----------

Suppose there is a file which content resembles the following

.. code-block:: none

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
