# Contribuindo

Obrigado pelo interesse em contribuir com o **cfinterface**! Esta página
resume os passos essenciais. Para instruções detalhadas, consulte a
[documentação completa de contribuição](https://rjmalves.github.io/cfinterface/getting_started/contributing.html).

## Reportando Bugs

Encontrou um comportamento inesperado? Abra uma
[issue no GitHub](https://github.com/rjmalves/cfinterface/issues) descrevendo
o problema. Inclua a versão do Python, o sistema operacional e um trecho de
código que permita reproduzir o erro.

## Enviando Pull Requests

Correções e melhorias são bem-vindas via
[pull request](https://github.com/rjmalves/cfinterface/pulls). Antes de
enviar, leia a documentação completa para garantir que o código segue as
convenções do projeto e que todos os testes e verificações de qualidade
passam.

## Configuracao Rapida

```bash
git clone https://github.com/rjmalves/cfinterface.git
cd cfinterface
uv sync --extra dev
uv run pre-commit install
```

## Documentacao Completa

Consulte a página de contribuição na documentação do projeto para detalhes
sobre hooks de pre-commit, convenções de código, execução de testes e build
da documentação:

<https://rjmalves.github.io/cfinterface/getting_started/contributing.html>
