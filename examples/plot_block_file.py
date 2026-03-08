"""
Lendo arquivos com BlockFile
=============================

Este exemplo demonstra como usar ``Block`` e ``BlockFile`` para ler e
escrever arquivos de texto estruturados em blocos delimitados por padrões
de início e fim.

Definimos dois tipos de bloco -- um para metadados do arquivo e outro para
registros de dados -- e realizamos o ciclo completo de leitura e escrita.
"""

# %%
# Definindo os tipos de bloco
# ----------------------------
# Cada subclasse de ``Block`` declara ``BEGIN_PATTERN`` (padrão de início)
# e ``END_PATTERN`` (padrão de fim) como expressões regulares. Os métodos
# ``read()`` e ``write()`` implementam a lógica de leitura e escrita.

import tempfile
from io import StringIO
from pathlib import Path
from typing import IO, Any

from cfinterface.components import Block
from cfinterface.files import BlockFile


class CabecalhoBloco(Block):
    """Bloco de cabeçalho com informações gerais do arquivo."""

    BEGIN_PATTERN = r"^CABECALHO"
    END_PATTERN = r"^FIM_CABECALHO"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # consome a linha BEGIN_PATTERN
        campos: dict[str, str] = {}
        while True:
            linha = file.readline()
            if not linha or self.__class__.ends(linha):
                break
            if "=" in linha:
                chave, _, valor = linha.partition("=")
                campos[chave.strip()] = valor.strip()
        self.data = campos
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("CABECALHO\n")
        for chave, valor in (self.data or {}).items():
            file.write(f"{chave} = {valor}\n")
        file.write("FIM_CABECALHO\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, CabecalhoBloco):
            return False
        return o.data == self.data


class DadosBloco(Block):
    """Bloco de dados com registros no formato chave=valor por linha."""

    BEGIN_PATTERN = r"^DADOS"
    END_PATTERN = r"^FIM_DADOS"

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.readline()  # consome a linha BEGIN_PATTERN
        registros: list[dict[str, str]] = []
        while True:
            linha = file.readline()
            if not linha or self.__class__.ends(linha):
                break
            linha = linha.strip()
            if not linha:
                continue
            campos = dict(
                par.split("=", 1) for par in linha.split("|") if "=" in par
            )
            campos = {k.strip(): v.strip() for k, v in campos.items()}
            if campos:
                registros.append(campos)
        self.data = registros
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        file.write("DADOS\n")
        for registro in self.data or []:
            linha = " | ".join(f"{k}={v}" for k, v in registro.items())
            file.write(f"{linha}\n")
        file.write("FIM_DADOS\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, DadosBloco):
            return False
        return o.data == self.data


# %%
# Definindo o modelo de arquivo
# ------------------------------
# A subclasse de ``BlockFile`` declara quais tipos de bloco o arquivo
# pode conter via ``BLOCKS``. Propriedades convenientes expõem os blocos
# por tipo usando ``data.get_blocks_of_type()``.


class MeuArquivoDeRegistros(BlockFile):
    BLOCKS = [CabecalhoBloco, DadosBloco]

    @property
    def cabecalho(self) -> CabecalhoBloco | None:
        return self.data.get_blocks_of_type(CabecalhoBloco)

    @property
    def registros(self) -> list[DadosBloco] | None:
        resultado = self.data.get_blocks_of_type(DadosBloco)
        if resultado is None:
            return None
        if isinstance(resultado, list):
            return resultado
        return [resultado]


# %%
# Escrevendo dados de exemplo e lendo de volta
# ---------------------------------------------
# Criamos um arquivo temporário com conteúdo conhecido, deixamos o
# framework fazer a leitura e verificamos os valores extraídos.

CONTEUDO_EXEMPLO = (
    "CABECALHO\n"
    "autor = joao.silva\n"
    "versao = 2.1\n"
    "data = 15/03/2025\n"
    "FIM_CABECALHO\n"
    "DADOS\n"
    "id=001 | nome=Produto A | preco=49.90\n"
    "id=002 | nome=Produto B | preco=129.00\n"
    "id=003 | nome=Produto C | preco=15.50\n"
    "FIM_DADOS\n"
    "DADOS\n"
    "id=101 | nome=Servico X | preco=299.00\n"
    "id=102 | nome=Servico Y | preco=199.00\n"
    "FIM_DADOS\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    caminho = Path(tmpdir) / "registros.txt"
    caminho.write_text(CONTEUDO_EXEMPLO, encoding="utf-8")

    arquivo = MeuArquivoDeRegistros.read(str(caminho))

    # Inspeciona o cabeçalho
    cab = arquivo.cabecalho
    print("=== Cabeçalho ===")
    for chave, valor in cab.data.items():
        print(f"  {chave}: {valor}")

    # Inspeciona os blocos de dados
    print(f"\n=== Blocos de Dados ({len(arquivo.registros)}) ===")
    for i, bloco in enumerate(arquivo.registros, start=1):
        print(f"  Bloco {i} ({len(bloco.data)} registros):")
        for reg in bloco.data:
            print(
                f"    id={reg['id']}  nome={reg['nome']}  preco={reg['preco']}"
            )

    # Escreve em um buffer de texto e verifica o round-trip
    buffer = StringIO()
    arquivo.write(buffer)
    conteudo_saida = buffer.getvalue()

    linhas_entrada = CONTEUDO_EXEMPLO.strip().splitlines()
    linhas_saida = conteudo_saida.strip().splitlines()
    print(
        f"\nRound-trip: {len(linhas_entrada)} linhas -> {len(linhas_saida)} linhas"
    )

# %%
# Escrevendo diretamente para arquivo
# -------------------------------------
# ``BlockFile.write()`` aceita tanto um caminho de arquivo quanto um
# objeto ``IO``, o que facilita a integração com pipelines existentes.

with tempfile.TemporaryDirectory() as tmpdir:
    caminho_entrada = Path(tmpdir) / "entrada.txt"
    caminho_saida = Path(tmpdir) / "saida.txt"

    caminho_entrada.write_text(CONTEUDO_EXEMPLO, encoding="utf-8")
    arquivo2 = MeuArquivoDeRegistros.read(str(caminho_entrada))
    arquivo2.write(str(caminho_saida))

    print(f"\nArquivo de saída criado: {caminho_saida.exists()}")
    print(f"Tamanho: {caminho_saida.stat().st_size} bytes")
