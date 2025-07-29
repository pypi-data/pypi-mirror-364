# PNCP

Ferramenta Python para facilitar pesquisas ao Portal Nacional de Contratações Públicas (PNCP).

## Instalação

Requer Python 3.12+. Recomenda-se instalar via pip ou [uv](https://github.com/astral-sh/uv):

```bash
pip install pncp
# ou
uv add pncp
```

## Exemplo de Uso

```python
from pncp.instrumentos_convocatorios import Busca

busca = Busca()

camara_dos_deputados = busca.listar_orgaos().filtrar(
    lambda o: "camara dos deputados" in o.nome.lower()
)

aviso_de_dispensa = busca.listar_instrumentos_convocatorios().filtrar(
    lambda i: "aviso" in i.nome.lower()
)

busca.preencher(
    orgaos=camara_dos_deputados, instrumentos_convocatorios=aviso_de_dispensa, anos=[2025]
)

print(busca.resultados)

if busca.resultados:
    resultado = busca.resultados[0]
    contratacao = resultado.detalhar()
    itens = contratacao.listar_itens()
    for item in itens:
        print(item)
```

## Funcionalidades

- Pesquisa órgãos e instrumentos convocatórios do PNCP
- Filtragem flexível por nome e atributos
- Detalhamento de contratações e itens
