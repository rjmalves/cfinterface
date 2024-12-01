Installation
=============

`cfinterface` is available for Python versions starting at `3.10`.

.. note::
   Installation as a root user is not recommended.
   Please setup a virtual environment, *e.g.*, via `venv <https://docs.python.org/3/library/venv.html>`_, `Anaconda or Miniconda <https://conda.io/projects/conda/en/latest/user-guide/install>`_, or create a `Docker image <https://www.docker.com/>`_. The easiest setup for you is probably with `uv <https://docs.astral.sh/uv/>`_.


Installation via PyPi
----------------------

To install `cfinterface` using `pip <https://packaging.python.org/en/latest/tutorials/installing-packages/>`_, run

.. code-block:: none

   pip install cfinterface

Installing directly from GitHub
--------------------------------

The `pip <https://packaging.python.org/en/latest/tutorials/installing-packages/>`_ syntax can be overloaded for installing directly from Git repositories. This is specially useful for testing development branches in your applications. Simply run 

.. code-block:: none

   pip install git+https://github.com/rjmalves/cfinterface.git

