Perguntas Frequentes (FAQ)
==========================

Esta pagina reune as duvidas mais comuns sobre o uso do ``cfinterface``,
organizadas por tema. Para detalhes completos sobre cada classe e metodo,
consulte a referencia da API na secao *Module Reference* e a
:doc:`visao geral da arquitetura </guides/architecture>`.

Quando usar Register, Block ou Section?
----------------------------------------

A escolha depende da estrutura do arquivo que voce precisa modelar:

- **Register** -- use quando cada linha relevante do arquivo e identificada
  por um prefixo fixo (ex.: ``"NR"``, ``"DA"``). O
  :class:`~cfinterface.components.register.Register` compara o inicio de cada
  linha contra o atributo ``IDENTIFIER`` para decidir qual tipo de registro
  processar. Use :class:`~cfinterface.files.registerfile.RegisterFile` como
  classe de arquivo.

- **Block** -- use quando os dados relevantes ficam entre uma linha de inicio
  e uma linha de fim identificaveis por expressoes regulares (ex.:
  ``BEGIN_PATTERN = r"^SECAO"`` e ``END_PATTERN = r"^FIM"``). O
  :class:`~cfinterface.components.block.Block` delega ao desenvolvedor a
  implementacao de ``read()`` e ``write()``. Use
  :class:`~cfinterface.files.blockfile.BlockFile` como classe de arquivo.

- **Section** -- use quando o arquivo e dividido em blocos ordenados e
  sequenciais, sem delimitadores de inicio e fim. Cada secao e processada na
  ordem em que aparece na lista ``SECTIONS`` da classe de arquivo. Use
  :class:`~cfinterface.files.sectionfile.SectionFile` como classe de arquivo.

Em resumo:

+------------------------+-------------------------------------------+
| Modelo                 | Quando usar                               |
+========================+===========================================+
| ``RegisterFile``       | Linhas com identificador de prefixo fixo  |
+------------------------+-------------------------------------------+
| ``BlockFile``          | Blocos com delimitadores de inicio e fim  |
+------------------------+-------------------------------------------+
| ``SectionFile``        | Secoes ordenadas sem delimitadores        |
+------------------------+-------------------------------------------+

Como lidar com arquivos binarios?
-----------------------------------

Defina ``STORAGE = StorageType.BINARY`` na sua classe de arquivo. O framework
abrira o arquivo em modo binario e delegara a leitura e escrita de cada campo
para os metodos ``_binary_read`` e ``_binary_write`` dos campos declarados.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MeuArquivoBinario(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = StorageType.BINARY
        ENCODING = "utf-8"

    arquivo = MeuArquivoBinario.read("/caminho/para/arquivo.bin")

Os campos nativos (:class:`~cfinterface.components.floatfield.FloatField` e
:class:`~cfinterface.components.integerfield.IntegerField`) ja implementam
``_binary_read`` e ``_binary_write`` usando ``numpy`` internamente. Para campos
customizados, voce deve implementar esses metodos ao subclassificar
:class:`~cfinterface.components.field.Field`.

.. note::

   Nunca use a string literal ``"BINARY"`` para o atributo ``STORAGE``. Esse
   uso esta depreciado desde a versao 1.9.0. Use sempre
   ``StorageType.BINARY``.

Como usar a integracao com pandas?
------------------------------------

O suporte a pandas e uma dependencia opcional. Instale com:

.. code-block:: bash

    pip install cfinterface[pandas]

Em seguida, utilize o metodo ``_as_df()`` disponivel em
:class:`~cfinterface.files.registerfile.RegisterFile` para obter um
:class:`pandas.DataFrame` com todos os registros de um determinado tipo:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile

    class MeuArquivo(RegisterFile):
        REGISTERS = [RegistroA, RegistroB]

    arquivo = MeuArquivo.read("/caminho/para/arquivo.txt")

    # Retorna um DataFrame com todas as instancias de RegistroA
    df = arquivo._as_df(RegistroA)
    print(df.head())

O metodo realiza um import lazily (somente quando chamado), portanto o
restante do codigo funciona normalmente mesmo sem pandas instalado. A
importacao so falha no momento em que ``_as_df()`` e invocado sem o pacote
presente.

Para dados tabulares dentro de secoes, o
:class:`~cfinterface.components.tabular.TabularParser` oferece o metodo
estatico :meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`:

.. code-block:: python

    from cfinterface.components.tabular import TabularParser

    dados = parser.parse_lines(linhas)
    df = TabularParser.to_dataframe(dados)

Como definir um campo personalizado?
--------------------------------------

Subclassifique :class:`~cfinterface.components.field.Field` e implemente os
quatro metodos abstratos. Os metodos ``_textual_read`` e ``_textual_write``
lidam com o modo texto; ``_binary_read`` e ``_binary_write`` lidam com o modo
binario.

.. code-block:: python

    from cfinterface.components.field import Field

    class BooleanField(Field):
        """Campo que representa um booleano como 'S'/'N' em texto
        ou 0x01/0x00 em binario."""

        def _textual_read(self, line: str) -> bool:
            token = line[self._starting_position:self._ending_position].strip()
            return token == "S"

        def _textual_write(self) -> str:
            return ("S" if self._value else "N").ljust(self._size)

        def _binary_read(self, line: bytes) -> bool:
            return line[self._starting_position:self._ending_position] == b"\x01"

        def _binary_write(self) -> bytes:
            return b"\x01" if self._value else b"\x00"

O campo pode ser usado em qualquer :class:`~cfinterface.components.line.Line`
da mesma forma que os campos nativos:

.. code-block:: python

    from cfinterface.components.line import Line

    linha = Line([BooleanField(size=1, starting_position=0)])
    valor = linha.read("S")  # True

Observe que ``_textual_write`` e ``_binary_write`` nao recebem argumentos
alem de ``self``: o valor a ser escrito e lido de ``self._value``.

Como resolver erros comuns de parsing?
----------------------------------------

**O valor de um campo retorna ``None``**

O campo nao conseguiu interpretar o conteudo da linha. Verifique se
``starting_position`` e ``size`` estao corretos para o arquivo real. O metodo
:meth:`~cfinterface.components.field.Field.read` captura ``ValueError`` e
retorna ``None`` quando a conversao falha.

**Erro de codificacao (``UnicodeDecodeError``)**

O arquivo usa uma codificacao diferente da listada em ``ENCODING``. Ajuste o
atributo ``ENCODING`` da classe de arquivo para incluir a codificacao correta:

.. code-block:: python

    class MeuArquivo(RegisterFile):
        REGISTERS = [...]
        ENCODING = ["latin-1", "utf-8"]  # tenta latin-1 primeiro

O framework tenta cada codificacao da lista em ordem e usa a primeira que
nao gerar erro.

**Registro nao encontrado no arquivo**

Verifique se ``IDENTIFIER`` e ``IDENTIFIER_DIGITS`` correspondem exatamente ao
prefixo no arquivo. ``IDENTIFIER_DIGITS`` deve ser igual ao numero de
caracteres (ou bytes, em modo binario) que formam o identificador. Um valor
errado faz com que o metodo
:meth:`~cfinterface.components.register.Register.matches` nunca retorne
``True``.

.. code-block:: python

    from cfinterface.components.register import Register
    from cfinterface.components.line import Line
    from cfinterface.components.literalfield import LiteralField

    class RegistroNome(Register):
        IDENTIFIER = "NM"       # exatamente 2 caracteres
        IDENTIFIER_DIGITS = 2   # deve coincidir com len(IDENTIFIER)
        LINE = Line([LiteralField(size=20, starting_position=2)])

Como usar o TabularParser?
---------------------------

:class:`~cfinterface.components.tabular.TabularParser` converte listas de
linhas de texto em um dicionario de listas indexado pelo nome da coluna, e
tambem oferece a operacao inversa.

O esquema de colunas e declarado com
:class:`~cfinterface.components.tabular.ColumnDef`. Cada ``ColumnDef`` precisa
de sua propria instancia de campo -- os campos sao mutados in-place durante a
leitura e nao podem ser compartilhados entre colunas.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    colunas = [
        ColumnDef(name="produto", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="preco", field=FloatField(size=10, starting_position=20, decimal_digits=2)),
    ]
    parser = TabularParser(colunas)

    linhas = [
        "Produto A               12.50     ",
        "Produto B                7.99     ",
    ]
    dados = parser.parse_lines(linhas)
    # {"produto": ["Produto A", "Produto B"], "preco": [12.5, 7.99]}

Para integracao com ``SectionFile``, use
:class:`~cfinterface.components.tabular.TabularSection` e declare apenas os
atributos de classe ``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN`` e
``DELIMITER``. Consulte o exemplo completo na galeria:
:ref:`sphx_glr_examples_plot_tabular_parsing.py`.

Como funciona o versionamento de arquivos?
-------------------------------------------

O versionamento permite que uma mesma classe de arquivo leia conteudo
produzido por versoes diferentes do esquema, sem necessidade de classes
separadas.

Declare o atributo de classe ``VERSIONS`` como um dicionario que mapeia chaves
de versao (strings comparadas lexicograficamente) a listas de tipos de
componentes:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class ArquivoVersionado(RegisterFile):
        REGISTERS = [RegistroV2A, RegistroV2B]  # esquema padrao (mais recente)
        VERSIONS = {
            "1.0": [RegistroV1A],
            "2.0": [RegistroV2A, RegistroV2B],
        }
        STORAGE = StorageType.TEXT

    # Seleciona o esquema da versao mais recente <= "1.5", ou seja, "1.0"
    arquivo = ArquivoVersionado.read("/caminho/arquivo.txt", version="1.5")

    # Valida se o conteudo lido corresponde ao esquema esperado
    resultado = arquivo.validate(version="1.0")
    print(resultado.matched)       # True se todos os tipos esperados foram encontrados
    print(resultado.missing_types) # tipos esperados que nao apareceram no arquivo

A funcao :func:`~cfinterface.versioning.resolve_version` faz a resolucao
lexicografica: dado ``version="1.5"`` e chaves ``["1.0", "2.0"]``, retorna
os componentes de ``"1.0"`` (a maior chave menor ou igual a ``"1.5"``).

Para exemplos completos de versionamento, consulte o exemplo da galeria:
:ref:`sphx_glr_examples_plot_versioned_file.py`.
