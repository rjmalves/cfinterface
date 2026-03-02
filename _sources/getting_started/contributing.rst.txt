Contributing
=============



.. note::
   If some not-expected behavior is found, the user is invited to open an `issue <https://github.com/rjmalves/cfinterface/issues>`_ at the repository. When doing so, it is recommended that some basic information (Python version, OS) is provided, together with a code snippet that allows reproducing the possible bug. However, if one found a possible fix for an existing issue, `pull requests <https://github.com/rjmalves/cfinterface/pulls>`_ are welcome. When doing so, please pay attention to the contents of this section.




Development dependencies
-------------------------

In order to install the required development dependencies, one might do::

    $ git clone https://github.com/rjmalves/inewave.git
    $ cd inewave
    $ pip install .[dev]

.. warning::

    The built docs content should not be moved into the repository. The assets are built and published by the `GitHub Actions <https://github.com/features/actions>`_ workflows in case of any change in the `main` branch.


Code conventions
----------------

This repository considers code quality tools in the CI workflows. Currently, only simples checks that ensure *static typing* and PEP8 converage are done. For testing, simple unit tests are done with `pytest <https://docs.pytest.org/en/stable/>`_.

Since these checks are in the CI workflows, for successfully publish a release, all the requirements must be met.

For ensure PEP8-compatible syntax, the `ruff <https://astral.sh/ruff>`_ module is recommended. Despite being a linter, and having a convenient `VSCode extension <https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff>`_, it is useful to ensure code quality via explicit CLI calls.

To ensure static typing, the `mypy <https://mypy-lang.org/>`_ module is recommended. This kind of typing reduces the amount of errors that might not be caught in unit tests and allows for better linter performance while coding.

To run the code quality checks that are executed in the CI environment, one might do::

    $ ruff check ./cfinterface
    $ mypy ./cfinterface


Testing
--------

The adopted framework for testing is `pytest <https://docs.pytest.org/en/stable/>`_.

Before doing a ``git push`` it is recommended that the user checks the tests locally, since they are fast and lightweighted. One can do this through::

    $ pytest ./tests
