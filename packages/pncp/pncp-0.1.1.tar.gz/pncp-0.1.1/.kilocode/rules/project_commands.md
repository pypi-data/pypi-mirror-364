# Comandos do Projeto e Ambiente de Execução

Este documento centraliza as diretrizes e exemplos para a execução de comandos dentro do ambiente do projeto.

## Uso Obrigatório do `uv run`

**IMPORTANTE:**
Todos os comandos deste projeto DEVEM ser executados com o prefixo `uv run`. Este prefixo garante que os comandos sejam executados no ambiente virtual correto, com as dependências do projeto devidamente configuradas.

**Exemplos:**
```bash
uv run pytest
uv run python seu_script.py
uv run task test
```

Qualquer comando sem o prefixo `uv run` não será reconhecido corretamente pelo ambiente do projeto e poderá resultar em erros ou comportamento inesperado.

Essas instruções são obrigatórias para qualquer automação, script ou interação via linha de comando.

## Executando Testes

Os testes da biblioteca estão localizados no diretório `tests/`. Para executar todos os testes do projeto, utilize o seguinte comando:

```bash
uv run task test
```

Alternativamente, para rodar o Pytest diretamente (se configurado no `pyproject.toml`):

```bash
uv run pytest
```

## Sobre o `uv`

[`uv`](https://github.com/astral-sh/uv) é um gerenciador de projetos Python e instalador de pacotes rápido. Recomenda-se seu uso para gerenciar dependências e executar comandos neste projeto, garantindo um ambiente consistente e performático.