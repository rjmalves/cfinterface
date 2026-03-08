"""
Lendo arquivos com SectionFile
================================

Este exemplo demonstra como usar ``Section`` e ``SectionFile`` para ler e
escrever arquivos de texto organizados em seções sequenciais.

Ao contrário de ``BlockFile`` (que busca blocos por padrão de início),
``SectionFile`` processa as seções em ordem fixa: cada seção lê o que
precisa do fluxo de caracteres e passa o controle para a próxima.
"""

# %%
# Definindo as seções
# --------------------
# Cada subclasse de ``Section`` implementa ``read()`` e ``write()`` para
# processar sua parte do arquivo. A leitura é sequencial -- a primeira
# seção lê o início do arquivo, a segunda lê a continuação, etc.

import tempfile
from io import StringIO
from pathlib import Path
from typing import IO, Any

from cfinterface.components import Section
from cfinterface.files import SectionFile


class SecaoCabecalho(Section):
    """Seção de cabeçalho: lê pares chave=valor até uma linha em branco."""

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        metadados: dict[str, str] = {}
        while True:
            linha = file.readline()
            if not linha or linha.strip() == "":
                break
            if "=" in linha:
                chave, _, valor = linha.partition("=")
                metadados[chave.strip()] = valor.strip()
        self.data = metadados
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        for chave, valor in (self.data or {}).items():
            file.write(f"{chave} = {valor}\n")
        file.write("\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SecaoCabecalho):
            return False
        return o.data == self.data


class SecaoTabela(Section):
    """Seção de tabela: lê linhas de dados separadas por '|' até EOF."""

    def __init__(self, previous=None, next=None, data=None) -> None:
        super().__init__(previous, next, data)

    def read(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        registros: list[list[str]] = []
        cabecalho: list[str] | None = None
        while True:
            linha = file.readline()
            if not linha:
                break
            linha = linha.strip()
            if not linha:
                continue
            colunas = [c.strip() for c in linha.split("|")]
            if cabecalho is None:
                cabecalho = colunas
            else:
                registros.append(colunas)
        self.data = {"cabecalho": cabecalho or [], "registros": registros}
        return True

    def write(self, file: IO[Any], *args: Any, **kwargs: Any) -> bool:
        dados = self.data or {"cabecalho": [], "registros": []}
        cabecalho = dados.get("cabecalho", [])
        registros = dados.get("registros", [])
        if cabecalho:
            file.write(" | ".join(cabecalho) + "\n")
        for reg in registros:
            file.write(" | ".join(reg) + "\n")
        return True

    def __eq__(self, o: object) -> bool:
        if not isinstance(o, SecaoTabela):
            return False
        return o.data == self.data


# %%
# Definindo o modelo de arquivo
# ------------------------------
# A subclasse de ``SectionFile`` declara a lista de seções em ``SECTIONS``
# na ordem em que aparecem no arquivo. Propriedades convenientes expõem
# cada seção por tipo via ``data.get_sections_of_type()``.


class MeuArquivoTabular(SectionFile):
    SECTIONS = [SecaoCabecalho, SecaoTabela]

    @property
    def cabecalho(self) -> SecaoCabecalho | None:
        return self.data.get_sections_of_type(SecaoCabecalho)

    @property
    def tabela(self) -> SecaoTabela | None:
        return self.data.get_sections_of_type(SecaoTabela)


# %%
# Escrevendo dados de exemplo e lendo de volta
# ---------------------------------------------
# Usamos um arquivo temporário com conteúdo conhecido para demonstrar
# o ciclo completo de leitura. A primeira seção (cabeçalho) consume os
# pares chave=valor seguidos de linha em branco; a segunda seção
# (tabela) consume o restante do arquivo.

CONTEUDO_EXEMPLO = (
    "titulo = Relatorio de Vendas\n"
    "responsavel = maria.souza\n"
    "periodo = 2025-Q1\n"
    "\n"
    "produto | quantidade | receita\n"
    "Widget A | 1200 | 59880.00\n"
    "Widget B | 850 | 127500.00\n"
    "Widget C | 430 | 21500.00\n"
    "Servico X | 60 | 18000.00\n"
)

with tempfile.TemporaryDirectory() as tmpdir:
    caminho = Path(tmpdir) / "relatorio.txt"
    caminho.write_text(CONTEUDO_EXEMPLO, encoding="utf-8")

    arquivo = MeuArquivoTabular.read(str(caminho))

    # Inspeciona o cabeçalho
    cab = arquivo.cabecalho
    print("=== Cabeçalho ===")
    for chave, valor in cab.data.items():
        print(f"  {chave}: {valor}")

    # Inspeciona a tabela
    tab = arquivo.tabela
    cabecalho_cols = tab.data["cabecalho"]
    registros = tab.data["registros"]

    print(f"\n=== Tabela ({len(registros)} registros) ===")
    print("  " + " | ".join(cabecalho_cols))
    print("  " + "-" * 50)
    for reg in registros:
        print("  " + " | ".join(reg))

# %%
# Round-trip via buffer de memória
# ---------------------------------
# ``SectionFile.write()`` aceita um objeto ``IO`` além de um caminho.
# Aqui escrevemos para um ``StringIO`` e confirmamos que o conteúdo
# foi preservado.

with tempfile.TemporaryDirectory() as tmpdir:
    caminho = Path(tmpdir) / "relatorio.txt"
    caminho.write_text(CONTEUDO_EXEMPLO, encoding="utf-8")

    arquivo2 = MeuArquivoTabular.read(str(caminho))

    buffer = StringIO()
    arquivo2.write(buffer)
    conteudo_saida = buffer.getvalue()

    linhas_entrada = CONTEUDO_EXEMPLO.strip().splitlines()
    linhas_saida = conteudo_saida.strip().splitlines()
    print(
        f"\nRound-trip: {len(linhas_entrada)} linhas entrada -> "
        f"{len(linhas_saida)} linhas saida"
    )

# %%
# Iterando sobre todas as seções
# --------------------------------
# ``SectionData`` é iterável: percorrer ``arquivo.data`` retorna todas
# as seções na ordem em que foram lidas, incluindo a seção padrão
# ``DefaultSection`` que ocupa o índice 0.

with tempfile.TemporaryDirectory() as tmpdir:
    caminho = Path(tmpdir) / "relatorio.txt"
    caminho.write_text(CONTEUDO_EXEMPLO, encoding="utf-8")

    arquivo3 = MeuArquivoTabular.read(str(caminho))

    print("\n=== Todas as seções ===")
    for sec in arquivo3.data:
        print(f"  {type(sec).__name__}")
