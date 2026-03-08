:orphan:

Visao Geral da Arquitetura
==========================

O ``cfinterface`` e um framework declarativo para construcao de interfaces de baixo nivel com
arquivos de texto ou binarios de estrutura complexa. Em vez de escrever codigo imperativo para
percorrer linhas de arquivo, o desenvolvedor declara o esquema -- quais campos existem, em quais
posicoes, como identificar cada registro -- e o framework cuida da leitura e escrita. Essa abordagem
torna o esquema do arquivo explicito, reutilizavel e testavel de forma independente.

O design segue um principio de composicao em camadas: componentes atomicos sao agrupados em
componentes intermediarios, que por sua vez sao orquestrados por classes de arquivo de alto nivel.
Uma camada de adaptadores isola as diferencas entre armazenamento textual e binario do restante do
codigo.

Hierarquia de Componentes
--------------------------

A hierarquia completa de componentes e ilustrada abaixo:

.. code-block:: text

    Field  (FloatField, IntegerField, LiteralField, DatetimeField)
      |
      v
    Line  (sequencia ordenada de Fields; delega I/O ao adaptador)
      |
      v
    Register / Block / Section  (componentes intermediarios; operam sobre handles de arquivo)
      |
      v
    RegisterFile / BlockFile / SectionFile  (classes de arquivo de alto nivel)

Cada camada depende apenas da camada imediatamente inferior, mantendo o acoplamento minimo e
permitindo que cada nivel seja testado e reutilizado de forma independente.

Campos (Fields)
----------------

:class:`cfinterface.components.field.Field` e a unidade atomica do framework. Um ``Field``
representa um unico valor posicional dentro de uma linha de arquivo: ele conhece sua posicao de
inicio (``starting_position``), seu tamanho em caracteres ou bytes (``size``) e o valor atual
(``value``). Os metodos publicos :meth:`~cfinterface.components.field.Field.read` e
:meth:`~cfinterface.components.field.Field.write` aceitam tanto ``str`` quanto ``bytes``,
delegando internamente para ``_textual_read``/``_binary_read`` ou
``_textual_write``/``_binary_write``.

O framework fornece quatro subclasses concretas prontas para uso:

:class:`cfinterface.components.floatfield.FloatField`
    Le e escreve numeros de ponto flutuante. Suporta notacoes fixa (``format="F"``),
    cientifica (``format="E"`` ou ``format="D"``) e separador decimal configuravel.
    Para armazenamento binario usa ``numpy`` (``float16``, ``float32`` ou ``float64``
    conforme o ``size``).

:class:`cfinterface.components.integerfield.IntegerField`
    Le e escreve inteiros. Em modo binario usa ``numpy`` (``int16``, ``int32`` ou ``int64``).

:class:`cfinterface.components.literalfield.LiteralField`
    Le e escreve strings de largura fixa, removendo espacos em branco nas extremidades ao ler
    e alinhando a esquerda ao escrever.

:class:`cfinterface.components.datetimefield.DatetimeField`
    Le e escreve objetos :class:`datetime.datetime` a partir de uma ou mais strings de formato.

Exemplo -- definindo um campo textual:

.. code-block:: python

    from cfinterface import LiteralField, FloatField

    nome = LiteralField(size=20, starting_position=0)
    saldo = FloatField(size=12, starting_position=20, decimal_digits=2)

    linha = "Conta Corrente       -1234.56    "
    nome.read(linha)    # "Conta Corrente"
    saldo.read(linha)   # -1234.56

Linha (Line)
-------------

:class:`cfinterface.components.line.Line` agrega uma lista ordenada de
:class:`~cfinterface.components.field.Field` e oferece os metodos
:meth:`~cfinterface.components.line.Line.read` e
:meth:`~cfinterface.components.line.Line.write` para operar sobre a linha inteira de uma so vez.
Internamente, ``Line`` nao realiza I/O diretamente: ela instancia um repositorio via a funcao
:func:`cfinterface.adapters.components.line.repository.factory`, passando o ``StorageType``
configurado. Esse repositorio e quem executa a leitura e escrita de acordo com o backend de
armazenamento (textual ou binario).

``Line`` aceita um ``delimiter`` opcional: quando informado, os campos sao separados por esse
caractere em vez de ocuparem posicoes fixas.

.. code-block:: python

    from cfinterface import LiteralField, FloatField
    from cfinterface.components.line import Line
    from cfinterface.storage import StorageType

    campos = [
        LiteralField(size=20, starting_position=0),
        FloatField(size=10, starting_position=20, decimal_digits=2),
    ]
    linha = Line(campos, storage=StorageType.TEXT)
    valores = linha.read("Conta Corrente      -1234.56  ")
    # valores == ["Conta Corrente", -1234.56]

Componentes Intermediarios
---------------------------

Os componentes intermediarios operam diretamente sobre handles de arquivo (``IO[Any]``) e
implementam a logica de identificacao e delimitacao de blocos de conteudo.

Register
~~~~~~~~~

:class:`cfinterface.components.register.Register` representa uma unica linha de arquivo
identificada por um prefixo fixo. O atributo de classe ``IDENTIFIER`` define o prefixo
(``str`` ou ``bytes``) e ``IDENTIFIER_DIGITS`` especifica o numero de caracteres ou bytes
que formam esse identificador. O atributo de classe ``LINE`` e uma instancia de
:class:`~cfinterface.components.line.Line` que descreve os campos apos o identificador.

O metodo de classe :meth:`~cfinterface.components.register.Register.matches` verifica se uma
linha pertence a esse tipo de registro comparando seu inicio com ``IDENTIFIER``.

.. code-block:: python

    from cfinterface.components.register import Register
    from cfinterface.components.line import Line
    from cfinterface.components.floatfield import FloatField

    class ValorMensal(Register):
        IDENTIFIER = "VM"
        IDENTIFIER_DIGITS = 2
        LINE = Line([FloatField(size=10, starting_position=2, decimal_digits=2)])

Block
~~~~~~

:class:`cfinterface.components.block.Block` representa um bloco delimitado por padroes de
inicio e fim. Os atributos de classe ``BEGIN_PATTERN`` e ``END_PATTERN`` sao expressoes
regulares (``str`` ou ``bytes``) que indicam onde o bloco comeca e termina. O atributo
``MAX_LINES`` (padrao: 10000) limita o numero de linhas processadas por bloco como
salvaguarda contra leituras infinitas.

Os metodos de classe :meth:`~cfinterface.components.block.Block.begins` e
:meth:`~cfinterface.components.block.Block.ends` testam uma linha contra os padroes
correspondentes. Os metodos :meth:`~cfinterface.components.block.Block.read` e
:meth:`~cfinterface.components.block.Block.write` devem ser implementados pela subclasse.

.. code-block:: python

    from cfinterface.components.block import Block

    class SecaoDados(Block):
        BEGIN_PATTERN = r"^INICIO"
        END_PATTERN = r"^FIM"

        def read(self, file, *args, **kwargs):
            # logica de leitura customizada
            return True

        def write(self, file, *args, **kwargs):
            # logica de escrita customizada
            return True

Section
~~~~~~~~

:class:`cfinterface.components.section.Section` representa uma divisao ordenada e sequencial
do arquivo, sem padroes de inicio ou fim. Sections sao processadas na ordem em que aparecem em
``SectionFile.SECTIONS``. O atributo de classe ``STORAGE`` (do tipo
:class:`~cfinterface.storage.StorageType`) indica se a secao opera em modo textual ou binario.
Os metodos :meth:`~cfinterface.components.section.Section.read` e
:meth:`~cfinterface.components.section.Section.write` devem ser implementados pela subclasse.

Classes de Arquivo
-------------------

As classes de arquivo sao o ponto de entrada do framework para o usuario final. Cada uma agrega
um conjunto de componentes intermediarios e fornece os metodos de alto nivel
:meth:`read`, :meth:`write`, :meth:`read_many` e :meth:`validate`.

:class:`cfinterface.files.registerfile.RegisterFile`
    Modela arquivos compostos por registros de linha unica. O atributo de classe ``REGISTERS``
    e uma lista de subclasses de :class:`~cfinterface.components.register.Register` na ordem
    em que podem aparecer no arquivo.

:class:`cfinterface.files.blockfile.BlockFile`
    Modela arquivos compostos por blocos delimitados. O atributo de classe ``BLOCKS`` e uma lista
    de subclasses de :class:`~cfinterface.components.block.Block`.

:class:`cfinterface.files.sectionfile.SectionFile`
    Modela arquivos compostos por secoes sequenciais. O atributo de classe ``SECTIONS`` e uma
    lista de subclasses de :class:`~cfinterface.components.section.Section`.

Atributos de classe comuns a todas as classes de arquivo:

``STORAGE``
    :class:`~cfinterface.storage.StorageType` que indica o backend de armazenamento
    (``StorageType.TEXT`` ou ``StorageType.BINARY``). Padrao: ``StorageType.TEXT``.

``ENCODING``
    Codificacao de texto a usar (``str``) ou lista de codificacoes tentadas em ordem
    (``list[str]``). Padrao: ``["utf-8", "latin-1", "ascii"]``.

``VERSIONS``
    Dicionario opcional que mapeia chaves de versao a listas de tipos de componentes,
    permitindo que um mesmo arquivo suporte multiplas versoes de esquema. Consulte a secao
    `Versionamento`_ para detalhes.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MeuArquivo(RegisterFile):
        REGISTERS = [ValorMensal]
        STORAGE = StorageType.TEXT
        ENCODING = "utf-8"

    arquivo = MeuArquivo.read("/caminho/para/arquivo.txt")
    arquivo.write("/caminho/para/saida.txt")

Camada de Adaptadores
----------------------

A camada de adaptadores isola as diferencas entre armazenamento textual e binario do restante do
framework. O modulo :mod:`cfinterface.adapters.components.repository` define a hierarquia:

- :class:`~cfinterface.adapters.components.repository.Repository` -- interface abstrata com
  metodos estaticos ``matches``, ``begins``, ``ends``, ``read`` e ``write``.
- :class:`~cfinterface.adapters.components.repository.TextualRepository` -- implementacao para
  arquivos de texto; usa ``file.readline()`` para leitura e comparacoes baseadas em regex
  sobre strings.
- :class:`~cfinterface.adapters.components.repository.BinaryRepository` -- implementacao para
  arquivos binarios; usa ``file.read(linesize)`` e comparacoes de bytes.

A funcao :func:`cfinterface.adapters.components.repository.factory` recebe um
:class:`~cfinterface.storage.StorageType` e retorna a classe de repositorio adequada.
Quando ``StorageType.TEXT`` e passado, retorna ``TextualRepository``; quando
``StorageType.BINARY``, retorna ``BinaryRepository``. Esse padrao de fabrica e o ponto central
que permite ao framework ser agnostico ao tipo de armazenamento.

As expressoes regulares usadas pelos adaptadores sao compiladas e armazenadas em cache na primeira
utilizacao (``_pattern_cache``), eliminando a recompilacao por chamada.

TabularParser
--------------

Introduzido na versao 1.9.0, :class:`cfinterface.components.tabular.TabularParser` oferece
uma abordagem declarativa para analisar conteudo tabular -- blocos de linhas onde cada linha
representa uma linha de dados com colunas definidas por posicoes fixas ou por um delimitador.

O esquema de colunas e declarado como uma lista de :class:`cfinterface.components.tabular.ColumnDef`,
uma ``NamedTuple`` com dois campos:

``name``
    Nome da coluna (chave no dicionario de saida).

``field``
    Instancia de :class:`~cfinterface.components.field.Field` que define o tipo, posicao e
    tamanho da coluna. Cada ``ColumnDef`` deve usar sua propria instancia de ``Field`` -- o
    metodo ``Line.read()`` muta os valores dos campos in-place, portanto compartilhar instancias
    entre colunas produz resultados incorretos.

Os metodos principais sao:

:meth:`~cfinterface.components.tabular.TabularParser.parse_lines`
    Recebe uma lista de strings e retorna um dicionario cujas chaves sao os nomes das colunas
    e cujos valores sao listas com os valores lidos linha a linha.

:meth:`~cfinterface.components.tabular.TabularParser.format_rows`
    Operacao inversa: recebe um dicionario no mesmo formato e retorna uma lista de strings
    formatadas.

:meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`
    Converte o dicionario resultante de ``parse_lines`` em um ``pandas.DataFrame``. Requer
    a dependencia opcional ``cfinterface[pandas]``.

Para uso integrado com ``SectionFile``, a classe
:class:`cfinterface.components.tabular.TabularSection` estende
:class:`~cfinterface.components.section.Section` e implementa ``read()`` e ``write()``
automaticamente com base nos atributos de classe ``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN``
e ``DELIMITER``.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    colunas = [
        ColumnDef(name="nome", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="valor", field=FloatField(size=10, starting_position=20, decimal_digits=2)),
    ]
    parser = TabularParser(colunas)

    linhas = [
        "Produto A               12.50     ",
        "Produto B                7.99     ",
    ]
    dados = parser.parse_lines(linhas)
    # dados == {"nome": ["Produto A", "Produto B"], "valor": [12.5, 7.99]}

Versionamento
--------------

O modulo :mod:`cfinterface.versioning` oferece suporte a arquivos cujo esquema evolui ao longo
do tempo, permitindo que uma mesma classe de arquivo leia conteudo de versoes diferentes sem
necessidade de classes separadas.

:class:`cfinterface.versioning.SchemaVersion`
    ``NamedTuple`` com tres campos: ``key`` (identificador de versao como string), ``components``
    (lista de tipos de componentes correspondentes a essa versao) e ``description`` (texto
    opcional).

``VERSIONS``
    Atributo de classe das classes de arquivo (``RegisterFile``, ``BlockFile``, ``SectionFile``).
    E um dicionario que mapeia chaves de versao (strings ordenadas lexicograficamente) a listas
    de tipos de componentes. Exemplo: ``{"1.0": [RegV1], "2.0": [RegV1, RegV2]}``.

:func:`cfinterface.versioning.resolve_version`
    Recebe uma chave de versao solicitada e o dicionario ``VERSIONS``. Retorna a lista de
    componentes cuja chave e a mais recente disponivel que seja menor ou igual a versao
    solicitada (comparacao lexicografica). Retorna ``None`` se a versao solicitada for anterior
    a todas as disponiveis.

:func:`cfinterface.versioning.validate_version`
    Valida o conteudo lido contra os tipos de componentes esperados. Retorna um
    :class:`~cfinterface.versioning.VersionMatchResult` com os campos ``matched``,
    ``expected_types``, ``found_types``, ``missing_types``, ``unexpected_types`` e
    ``default_ratio``.

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class ArquivoVersionado(RegisterFile):
        REGISTERS = [ValorMensalV2]
        VERSIONS = {
            "1.0": [ValorMensalV1],
            "2.0": [ValorMensalV2],
        }
        STORAGE = StorageType.TEXT

    # Leitura selecionando versao sem mutar a classe
    arquivo = ArquivoVersionado.read("/caminho/arquivo.txt", version="1.5")
    # resolve_version("1.5", VERSIONS) retornara os componentes de "1.0"

    # Validacao do conteudo lido
    resultado = arquivo.validate(version="1.0")
    print(resultado.matched)  # True se o conteudo corresponde ao esquema 1.0

StorageType
------------

:class:`cfinterface.storage.StorageType` e uma enumeracao (``str``, ``Enum``) que substitui o
uso de strings literais ``"TEXT"`` e ``"BINARY"`` para identificar o backend de armazenamento.
Ela herda de ``str``, o que garante compatibilidade retroativa: ``StorageType.TEXT == "TEXT"``
e ``True``.

Os dois valores disponiveis sao:

``StorageType.TEXT``
    Indica armazenamento textual. O arquivo e aberto em modo texto e as operacoes usam
    ``str``.

``StorageType.BINARY``
    Indica armazenamento binario. O arquivo e aberto em modo binario e as operacoes usam
    ``bytes``.

O uso de strings literais ``"TEXT"`` e ``"BINARY"`` no atributo ``STORAGE`` das classes de
arquivo esta depreciado desde a versao 1.9.0. A funcao interna ``_ensure_storage_type`` emite
um :class:`DeprecationWarning` quando uma string simples e detectada no lugar de um membro da
enumeracao.

.. code-block:: python

    from cfinterface.storage import StorageType

    # Correto -- use sempre a enumeracao
    class MeuArquivoBinario(RegisterFile):
        REGISTERS = [...]
        STORAGE = StorageType.BINARY

    # Depreciado -- nao usar
    # STORAGE = "BINARY"

Pontos de Extensao
-------------------

O ``cfinterface`` foi projetado para ser estendido por subclasses. Os principais pontos de
extensao para desenvolvedores de bibliotecas downstream sao:

Subclasses de Field
~~~~~~~~~~~~~~~~~~~~

Crie uma subclasse de :class:`~cfinterface.components.field.Field` para suportar tipos de dados
nao cobertos pelas implementacoes nativas. Implemente os quatro metodos abstratos:
``_textual_read``, ``_binary_read``, ``_textual_write`` e ``_binary_write``.

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

Subclasses de Register
~~~~~~~~~~~~~~~~~~~~~~~

Declare ``IDENTIFIER``, ``IDENTIFIER_DIGITS`` e ``LINE`` para definir um novo tipo de registro
identificado por prefixo. Nenhum metodo precisa ser sobrescrito para o caso padrao de leitura e
escrita posicional.

Subclasses de Block
~~~~~~~~~~~~~~~~~~~~

Declare ``BEGIN_PATTERN`` e ``END_PATTERN`` e implemente ``read()`` e ``write()`` com a logica
de processamento especifica para o bloco.

Subclasses de Section
~~~~~~~~~~~~~~~~~~~~~~

Declare ``STORAGE`` e implemente ``read()`` e ``write()``. Para secoes tabulares, prefira
subclassificar :class:`~cfinterface.components.tabular.TabularSection` e declarar apenas
``COLUMNS``, ``HEADER_LINES``, ``END_PATTERN`` e ``DELIMITER``.

Dicionarios VERSIONS
~~~~~~~~~~~~~~~~~~~~~

Adicione o atributo de classe ``VERSIONS`` a qualquer subclasse de
:class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile` ou
:class:`~cfinterface.files.sectionfile.SectionFile` para habilitar a selecao de esquema por
versao em tempo de leitura, sem necessidade de criar subclasses separadas para cada versao.

TabularParser com schemas personalizados
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instancie :class:`~cfinterface.components.tabular.TabularParser` com uma lista de
:class:`~cfinterface.components.tabular.ColumnDef` para analisar qualquer bloco tabular, seja
de largura fixa ou delimitado. A mesma instancia pode ser reutilizada para multiplos arquivos
com o mesmo esquema.
