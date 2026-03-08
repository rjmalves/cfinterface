:orphan:

Dicas de Performance
====================

O ``cfinterface`` v1.9.0 inclui diversas otimizacoes internas que melhoram o
desempenho em cenarios de leitura e escrita de arquivos. Alem dessas
melhorias automaticas, existem padroes de uso que permitem ao desenvolvedor
extrair ainda mais performance ao modelar arquivos com o framework.

Esta pagina descreve as otimizacoes internas e orienta como aproveita-las
por meio de escolhas conscientes de design.

Cache de Regex nos Adaptadores
-------------------------------

Nas versoes anteriores, cada chamada de leitura que usava um padrao de
expressao regular recompilava o padrao a partir da string original. A partir
da v1.9.0, o modulo de adaptadores mantem um dicionario global
``_pattern_cache`` que armazena os objetos compilados de cada padrao apos o
primeiro uso.

O impacto e transparente para o usuario: o mesmo padrao passado em
``BEGIN_PATTERN`` ou ``END_PATTERN`` de um
:class:`~cfinterface.components.block.Block` e compilado uma unica vez, por
mais vezes que o arquivo seja lido durante a execucao do programa.

Nao e necessario nenhuma acao adicional; o cache e automatico. O unico
cuidado e manter os padroes como strings literais estaveis na definicao da
classe, evitando a construcao de padroes dinamicos em tempo de execucao, que
gerariam entradas distintas no cache e anulariam o beneficio.

.. code-block:: python

    from cfinterface.components.block import Block

    class MeuBloco(Block):
        # Padrao compilado uma vez e reutilizado em todas as leituras
        BEGIN_PATTERN = r"^INICIO"
        END_PATTERN = r"^FIM"

Otimizacao do FloatField
-------------------------

O metodo ``_textual_write()`` do
:class:`~cfinterface.components.floatfield.FloatField` foi reescrito para
realizar no maximo tres tentativas de formatacao, independente do valor de
``decimal_digits``. A implementacao anterior percorria um loop de tamanho
O(decimal_digits) para encontrar o numero de casas decimais que cabe no campo.

Para aproveitar ao maximo essa otimizacao, declare ``size`` e
``decimal_digits`` com os valores minimos necessarios para representar os
valores do seu dominio. Campos superdimensionados ainda funcionam corretamente,
mas campos ajustados ao valor real eliminam tentativas de formatacao
desnecessarias.

.. code-block:: python

    from cfinterface.components.floatfield import FloatField
    from cfinterface.components.line import Line

    # Preferir tamanho ajustado ao dominio do valor
    campo_preco = FloatField(size=10, starting_position=0, decimal_digits=2)

    # Evitar campos excessivamente grandes sem necessidade
    # campo_preco = FloatField(size=30, starting_position=0, decimal_digits=15)

    linha = Line([campo_preco])

Containers Baseados em Array
-----------------------------

As classes de container
:class:`~cfinterface.data.registerdata.RegisterData`,
``BlockData`` e ``SectionData`` foram migradas de estruturas encadeadas
(linked-list) para listas Python (``list``) com indice auxiliar por tipo.

As principais consequencias praticas sao:

- ``len()`` agora e O(1) ao inves de O(n) na implementacao anterior
- Iteracao sobre todos os elementos continua sendo O(n), porem com melhor
  localidade de memoria (elementos contiguos em memoria)
- As propriedades ``previous`` e ``next`` de registros, blocos e secoes sao
  agora calculadas a partir da posicao no container, sem custo de armazenamento
  adicional

Esse ganho e automatico para qualquer codigo que use as classes de arquivo
existentes sem modificacao.

Leitura em Lote com read_many()
---------------------------------

Quando e necessario ler multiplos arquivos do mesmo tipo, o padrao de loop
com instanciacao individual pode ser substituido pelo metodo de classe
:meth:`~cfinterface.files.registerfile.RegisterFile.read_many`, disponivel
em :class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile` e
:class:`~cfinterface.files.sectionfile.SectionFile`.

.. code-block:: python

    # Antes: leitura individual em loop
    from meu_modulo import MeuArquivo

    arquivos = []
    for caminho in caminhos:
        f = MeuArquivo.read(caminho)
        arquivos.append(f)

.. code-block:: python

    # Depois: leitura em lote com read_many()
    from meu_modulo import MeuArquivo

    # Retorna um dict[str, MeuArquivo] keyed pelo caminho
    arquivos = MeuArquivo.read_many(caminhos)

    # Acesso por caminho
    arquivo = arquivos["/caminho/para/arquivo.txt"]

O metodo ``read_many()`` aceita o parametro opcional ``version`` para
selecionar o esquema de versionamento, da mesma forma que ``read()``:

.. code-block:: python

    arquivos = MeuArquivo.read_many(caminhos, version="1.0")

Selecao de Colunas no TabularParser
-------------------------------------

O :class:`~cfinterface.components.tabular.TabularParser` analisa linhas de
texto posicionais (ou delimitadas) e converte cada coluna declarada em uma
lista de valores. Em arquivos tabulares grandes, declarar apenas as colunas
necessarias reduz o trabalho de conversao de tipos para cada linha lida.

Use :class:`~cfinterface.components.tabular.ColumnDef` para listar somente
as colunas de interesse, omitindo as demais:

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField
    from cfinterface.components.integerfield import IntegerField

    # Arquivo tem 5 colunas; apenas 2 sao necessarias
    colunas_necessarias = [
        ColumnDef(name="codigo", field=LiteralField(size=8, starting_position=0)),
        ColumnDef(name="valor", field=FloatField(size=12, starting_position=20, decimal_digits=4)),
        # As colunas nas posicoes 8-19 e 32+ sao simplesmente ignoradas
    ]

    parser = TabularParser(colunas_necessarias)
    dados = parser.parse_lines(linhas)
    # {"codigo": [...], "valor": [...]}

Para secoes tabulares integradas ao framework, declare apenas as colunas
necessarias no atributo de classe ``COLUMNS`` da sua subclasse de
:class:`~cfinterface.components.tabular.TabularSection`:

.. code-block:: python

    from cfinterface.components.tabular import TabularSection, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    class SecaoDados(TabularSection):
        COLUMNS = [
            ColumnDef(name="id", field=LiteralField(size=8, starting_position=0)),
            ColumnDef(name="resultado", field=FloatField(size=12, starting_position=20, decimal_digits=3)),
        ]
        HEADER_LINES = 1
        END_PATTERN = r"^---"

Dicas Gerais
-------------

As dicas a seguir complementam as otimizacoes internas descritas acima e
se aplicam a qualquer codigo que use o ``cfinterface``.

**Reutilize instancias de classe de arquivo para multiplas leituras**

O metodo ``read()`` e um metodo de classe que retorna uma nova instancia a
cada chamada. Quando o mesmo arquivo precisa ser lido novamente (por exemplo,
apos uma escrita), prefira guardar e reutilizar a instancia existente ou
use ``read_many()`` para um conjunto de caminhos conhecidos de uma vez.

**Use o enum StorageType ao inves de strings literais**

O atributo ``STORAGE`` aceita tanto strings (``"TEXT"``, ``"BINARY"``) quanto
o enum :class:`~cfinterface.storage.StorageType`. O uso de strings esta
depreciado desde a v1.9.0 e emite um aviso em tempo de execucao. Prefira
sempre o enum:

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MeuArquivo(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = StorageType.TEXT  # correto
        # STORAGE = "TEXT"  # depreciado; evitar

**Declare ENCODING como string unica quando a codificacao e conhecida**

O atributo ``ENCODING`` aceita uma string unica ou uma lista de strings. Quando
passado como lista, o framework tenta cada codificacao em ordem ate que uma
leitura seja bem-sucedida. Se a codificacao do arquivo e conhecida e fixa,
declare ``ENCODING`` como uma string diretamente para eliminar as tentativas
desnecessarias:

.. code-block:: python

    class MeuArquivo(RegisterFile):
        REGISTERS = [MeuRegistro]
        ENCODING = "latin-1"           # leitura direta, sem tentativas extras
        # ENCODING = ["latin-1", "utf-8"]  # necessario apenas quando a
        #                                   # codificacao pode variar
