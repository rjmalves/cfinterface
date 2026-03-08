Guia de Migracao: v1.8.x para v1.9.0
======================================

O cfinterface v1.9.0 e uma versao de funcionalidades com algumas mudancas
incompativeis para projetos downstream. Este guia cobre todas as alteracoes
que exigem modificacao de codigo existente -- mudancas de dependencias,
substituicoes de API e comportamentos depreciados -- bem como as novas
funcionalidades opcionais que os usuarios podem adotar no seu proprio ritmo.

Leia cada secao e aplique as alteracoes correspondentes ao seu projeto antes
de atualizar a dependencia para ``cfinterface>=1.9.0``. O `Checklist de
Migracao`_ no final resume os passos em ordem.

pandas como Dependencia Opcional
---------------------------------

**O que mudou:** pandas deixou de ser uma dependencia obrigatoria do
cfinterface. A partir da versao 1.9.0, somente ``numpy>=2.0.0`` e exigido em
tempo de execucao. O pandas e instalado apenas quando o extra ``[pandas]`` e
solicitado explicitamente.

Esta mudanca reduz o tamanho do ambiente de instalacao para projetos que nao
utilizam :meth:`~cfinterface.files.registerfile.RegisterFile._as_df` ou
:meth:`~cfinterface.components.tabular.TabularParser.to_dataframe`.

Antes (v1.8.x):

.. code-block:: python

    # pandas era instalado automaticamente com cfinterface
    pip install cfinterface

Depois (v1.9.0):

.. code-block:: python

    # Instale o extra [pandas] apenas se precisar de integracao com DataFrame
    pip install cfinterface[pandas]

Se o seu projeto importa ``pandas`` diretamente a partir de codigo que assume
que cfinterface o instalou, adicione ``pandas`` como dependencia explicita do
seu projeto ou instale o extra:

.. code-block:: python

    # Antes: import implicito que funcionava porque cfinterface trazia pandas
    import pandas as pd
    df = pd.DataFrame(arquivo.data)

    # Depois: instale cfinterface[pandas] ou declare pandas como dependencia
    # propria do seu projeto
    import pandas as pd  # requer pip install cfinterface[pandas]
    df = pd.DataFrame(arquivo.data)

StorageType Enum
-----------------

**O que mudou:** O atributo de classe ``STORAGE`` das classes de arquivo
(:class:`~cfinterface.files.registerfile.RegisterFile`,
:class:`~cfinterface.files.blockfile.BlockFile`,
:class:`~cfinterface.files.sectionfile.SectionFile`) deve agora usar
:class:`~cfinterface.storage.StorageType` em vez de strings literais.
O uso de strings ``"TEXT"`` ou ``"BINARY"`` emite um
:class:`DeprecationWarning` em tempo de execucao e sera removido em uma
versao futura.

:class:`~cfinterface.storage.StorageType` herda de ``str``, de modo que
``StorageType.TEXT == "TEXT"`` e ``True``. Codigo que apenas *le* o valor
de ``STORAGE`` e compara com strings continua funcionando sem alteracoes.

Antes (v1.8.x):

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile

    class MeuArquivo(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = "TEXT"  # string literal -- depreciado

    class MeuArquivoBinario(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = "BINARY"  # string literal -- depreciado

Depois (v1.9.0):

.. code-block:: python

    from cfinterface.files.registerfile import RegisterFile
    from cfinterface.storage import StorageType

    class MeuArquivo(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = StorageType.TEXT  # enum -- correto

    class MeuArquivoBinario(RegisterFile):
        REGISTERS = [MeuRegistro]
        STORAGE = StorageType.BINARY  # enum -- correto

Deprecacao de set_version()
-----------------------------

**O que mudou:** O metodo de classe ``set_version()`` esta depreciado. Ele
mutava o estado da classe de forma permanente, o que causava comportamento
inesperado em aplicacoes que liam versoes diferentes do mesmo arquivo em
sequencia. O argumento ``version=`` no metodo :meth:`read` substitui essa
funcionalidade de forma segura e sem efeitos colaterais.

Antes (v1.8.x):

.. code-block:: python

    from meu_projeto.arquivos import MeuArquivoVersionado

    # set_version() mutava a classe permanentemente
    MeuArquivoVersionado.set_version("1.0")
    arquivo_v1 = MeuArquivoVersionado.read("dados_v1.txt")

    MeuArquivoVersionado.set_version("2.0")
    arquivo_v2 = MeuArquivoVersionado.read("dados_v2.txt")

Depois (v1.9.0):

.. code-block:: python

    from meu_projeto.arquivos import MeuArquivoVersionado

    # version= e passado diretamente para read(); a classe nao e mutada
    arquivo_v1 = MeuArquivoVersionado.read("dados_v1.txt", version="1.0")
    arquivo_v2 = MeuArquivoVersionado.read("dados_v2.txt", version="2.0")

O argumento ``version=`` e suportado por todos os tres tipos de arquivo:
:meth:`~cfinterface.files.registerfile.RegisterFile.read`,
:meth:`~cfinterface.files.blockfile.BlockFile.read` e
:meth:`~cfinterface.files.sectionfile.SectionFile.read`.

Containers Baseados em Array
------------------------------

**O que mudou:** As classes de container de dados
(:class:`~cfinterface.data.registerdata.RegisterData`,
:class:`~cfinterface.data.blockdata.BlockData`,
:class:`~cfinterface.data.sectiondata.SectionData`) foram migradas de
estruturas de lista encadeada para containers baseados em array (``list``
Python). As principais consequencias praticas sao:

- **``len()`` e agora O(1).** Em versoes anteriores, calcular o tamanho da
  colecao exigia percorrer a cadeia de ponteiros.
- **``previous`` e ``next`` sao propriedades computadas,** nao atributos
  armazenados. Os valores sao derivados da posicao do elemento no array
  interno. O comportamento observavel e identico, mas codigo que atribuia
  diretamente a ``register.previous`` ou ``register.next`` para reorganizar
  elementos nao funciona mais como esperado -- use os metodos do container
  (:meth:`~cfinterface.data.registerdata.RegisterData.add_before`,
  :meth:`~cfinterface.data.registerdata.RegisterData.add_after`,
  :meth:`~cfinterface.data.registerdata.RegisterData.remove`) em vez disso.
- **O padrao de acesso primario permanece o mesmo.** Iteracao direta e o
  metodo :meth:`~cfinterface.data.registerdata.RegisterData.of_type` continuam
  funcionando sem alteracoes.

Se o seu codigo dependia de atribuir ``previous``/``next`` como ponteiros
armazenados, refatore para usar os metodos de mutacao do container:

.. code-block:: python

    # Antes (v1.8.x): manipulacao direta de ponteiros
    novo_registro.next = registro_existente
    novo_registro.previous = registro_existente.previous
    # ... encadeamento manual ...

    # Depois (v1.9.0): use os metodos do container
    arquivo.data.add_before(registro_existente, novo_registro)

O padrao de leitura tipico continua identico:

.. code-block:: python

    # Este padrao funciona igual em v1.8.x e v1.9.0
    for registro in arquivo.data.of_type(MeuRegistro):
        print(registro.valor)

Novas Funcionalidades
----------------------

As funcionalidades a seguir sao adicionais e nao requerem alteracoes em
codigo existente. Adote-as conforme a necessidade do seu projeto.

TabularParser e ColumnDef
~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`cfinterface.components.tabular.TabularParser` oferece uma abordagem
declarativa para analisar blocos de conteudo tabular -- tanto de largura fixa
quanto delimitados. O esquema de colunas e declarado como uma lista de
:class:`cfinterface.components.tabular.ColumnDef`.

.. code-block:: python

    from cfinterface.components.tabular import TabularParser, ColumnDef
    from cfinterface.components.literalfield import LiteralField
    from cfinterface.components.floatfield import FloatField

    colunas = [
        ColumnDef(name="nome", field=LiteralField(size=20, starting_position=0)),
        ColumnDef(name="valor", field=FloatField(size=10, starting_position=20,
                                                 decimal_digits=2)),
    ]
    parser = TabularParser(colunas)
    dados = parser.parse_lines(["Produto A               12.50     "])
    # {"nome": ["Produto A"], "valor": [12.5]}

A classe :class:`~cfinterface.components.tabular.TabularSection` facilita a
integracao de blocos tabulares em ``SectionFile``.

read_many() -- Leitura em Lote
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:meth:`~cfinterface.files.registerfile.RegisterFile.read_many` le multiplos
arquivos em uma unica chamada e retorna um dicionario indexado pelo caminho:

.. code-block:: python

    arquivos = MeuArquivo.read_many(
        ["/dados/jan.txt", "/dados/fev.txt", "/dados/mar.txt"]
    )
    # {"./dados/jan.txt": <MeuArquivo>, ...}

O argumento ``version=`` tambem e aceito por ``read_many()``.

SchemaVersion e validate_version()
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:class:`cfinterface.versioning.SchemaVersion` e
:func:`cfinterface.versioning.validate_version` permitem declarar versoes de
esquema de forma estruturada e verificar programaticamente se o conteudo lido
corresponde ao esquema esperado:

.. code-block:: python

    resultado = arquivo.validate(version="2.0")
    if not resultado.matched:
        print("Tipos ausentes:", resultado.missing_types)

py.typed -- PEP 561
~~~~~~~~~~~~~~~~~~~~~

O marcador ``py.typed`` foi adicionado ao pacote, habilitando verificacao de
tipos downstream com mypy, pyright e ferramentas similares. Nenhuma alteracao
de codigo e necessaria; o beneficio e automatico ao atualizar para v1.9.0.

Checklist de Migracao
-----------------------

Siga os passos abaixo em ordem para migrar um projeto de v1.8.x para v1.9.0:

1. Atualize a dependencia no seu ``pyproject.toml`` ou ``requirements.txt``
   para ``cfinterface>=1.9.0``.

2. Se o seu projeto utiliza pandas (``_as_df()``, ``to_dataframe()`` ou
   qualquer importacao indireta via cfinterface), altere a dependencia para
   ``cfinterface[pandas]>=1.9.0`` ou adicione ``pandas`` como dependencia
   explicita do seu projeto.

3. Substitua todas as ocorrencias de ``STORAGE = "TEXT"`` por
   ``STORAGE = StorageType.TEXT`` e ``STORAGE = "BINARY"`` por
   ``STORAGE = StorageType.BINARY`` nas suas subclasses de arquivo. Adicione
   o import ``from cfinterface.storage import StorageType`` nos arquivos
   afetados.

4. Substitua todas as chamadas a ``set_version()`` pelo argumento ``version=``
   em :meth:`read`. Exemplo: ``MinhaClasse.set_version("1.0"); MinhaClasse.read(path)``
   vira ``MinhaClasse.read(path, version="1.0")``.

5. Verifique se algum codigo do seu projeto atribui diretamente aos atributos
   ``previous`` ou ``next`` de registros, blocos ou secoes com o intuito de
   reorganizar elementos no container. Substitua essas operacoes pelos metodos
   :meth:`~cfinterface.data.registerdata.RegisterData.add_before`,
   :meth:`~cfinterface.data.registerdata.RegisterData.add_after` ou
   :meth:`~cfinterface.data.registerdata.RegisterData.remove`.

6. Execute a suite de testes do seu projeto para confirmar compatibilidade.
   Preste atencao a :class:`DeprecationWarning` nos logs -- eles indicam
   padroes depreciados que ainda funcionam mas devem ser corrigidos antes de
   uma versao futura.
