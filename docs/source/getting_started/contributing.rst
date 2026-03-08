Contribuindo
=============

Para reportar comportamentos inesperados, abra uma
`issue <https://github.com/rjmalves/cfinterface/issues>`_ no repositório.
Ao fazê-lo, recomenda-se fornecer informações básicas (versão do Python,
sistema operacional) junto com um trecho de código que permita reproduzir
o problema. Caso tenha encontrado uma possível correção para um problema
existente, `pull requests <https://github.com/rjmalves/cfinterface/pulls>`_
são bem-vindos. Nesse caso, atente-se ao conteúdo desta página antes de
enviar a contribuição.


Configuracao do Ambiente de Desenvolvimento
--------------------------------------------

Para instalar as dependências de desenvolvimento, execute os comandos abaixo:

.. code-block:: bash

    git clone https://github.com/rjmalves/cfinterface.git
    cd cfinterface
    uv sync --extra dev
    uv run pre-commit install


Hooks de Pre-commit
--------------------

O projeto utiliza `pre-commit <https://pre-commit.com/>`_ para garantir a
qualidade do código automaticamente antes de cada commit. São três hooks
configurados:

- **ruff** (v0.9.10): linter com correção automática (``--fix``)
- **ruff-format** (v0.9.10): formatação de código
- **mypy** (v1.19.1): verificação de tipos estáticos, aplicada apenas ao
  diretório ``cfinterface/``

Para executar todos os hooks manualmente sobre todos os arquivos:

.. code-block:: bash

    uv run pre-commit run --all-files


Convencoes de Codigo
---------------------

O projeto utiliza ``ruff`` para lint e formatação, e ``mypy`` para tipagem
estática. Para executar as verificações manualmente:

.. code-block:: bash

    uv run ruff check ./cfinterface
    uv run ruff format --check ./cfinterface
    uv run mypy ./cfinterface

Essas mesmas verificações são executadas nos workflows de CI. Para que uma
versão seja publicada com sucesso, todos os requisitos devem ser atendidos.


Testes
-------

O framework de testes adotado é o `pytest <https://docs.pytest.org/en/stable/>`_.

Para executar todos os testes:

.. code-block:: bash

    uv run pytest ./tests

Para executar apenas os testes de performance com
`pytest-benchmark <https://pytest-benchmark.readthedocs.io/>`_:

.. code-block:: bash

    uv run pytest ./tests --benchmark-only

Para verificar a cobertura de testes com
`pytest-cov <https://pytest-cov.readthedocs.io/>`_:

.. code-block:: bash

    uv run pytest ./tests --cov=cfinterface


Documentacao
-------------

A documentação é construída com `Sphinx <https://www.sphinx-doc.org/>`_ e o
tema `Furo <https://pradyunsg.me/furo/>`_. Para gerar a documentação
localmente:

.. code-block:: bash

    uv run sphinx-build -W -b html docs/source docs/build/html

.. note::

    O conteúdo gerado pela build **não deve ser commitado** no repositório.
    Os artefatos são construídos e publicados automaticamente pelos workflows
    do `GitHub Actions <https://github.com/features/actions>`_ a cada
    alteração na branch ``main``.
