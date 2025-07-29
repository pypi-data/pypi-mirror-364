# Biblioteca Python PNCP

## Visão Geral do Projeto

Esta biblioteca oferece uma interface Python para consultar e processar dados de compras públicas a partir da API do PNCP (Portal Nacional de Contratações Públicas) do Brasil. Permite filtrar, buscar e obter informações detalhadas sobre instrumentos convocatórios, órgãos e entidades relacionadas.

## Uso da API

### Exemplo de Fluxo

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
    orgaos=camara_dos_deputados,
    instrumentos_convocatorios=aviso_de_dispensa,
    anos=[2025]
)

print(busca.resultados)
```

#### Exemplo: Acessando uma Contratação e seus Itens

Este exemplo mostra como acessar uma contratação específica a partir dos resultados e listar seus itens detalhadamente. Isso é útil para obter informações completas sobre uma contratação e seus componentes.

```python
# Seleciona o primeiro resultado da busca
resultado = busca.resultados[0]

# Obtém o objeto Contratacao detalhado
contratacao = resultado.detalhar()  # [`detalhar()`](src/pncp/instrumentos_convocatorios/tipos.py:154)

# Lista os itens associados à contratação
itens = contratacao.listar_itens()  # [`listar_itens()`](src/pncp/instrumentos_convocatorios/tipos.py:244)

# Itera e imprime os itens
for item in itens:
    print(item)
```

### Conceitos Principais

-   **Instanciação**: Crie um objeto `Busca`.
-   **Listagem**: Utilize métodos como `listar_orgaos()` e `listar_instrumentos_convocatorios()` para obter listas de entidades.
-   **Filtragem**: Use `.filtrar()` nas listas para selecionar itens relevantes.
-   **Preencher**: Use `busca.preencher(...)` para definir os parâmetros da busca.
-   **Resultados**: Acesse `busca.resultados` para obter os resultados.
-   **Detalhamento**: Use `resultado.detalhar()` para obter informações completas da contratação.
-   **Itens**: Use `contratacao.listar_itens()` para acessar os itens da contratação.

## Componentes Principais

-   [`Busca`](src/pncp/instrumentos_convocatorios/busca.py:24): Classe principal para construir e executar consultas. Oferece métodos para listar e filtrar entidades, definir parâmetros de busca e obter resultados.
-   [`Lista`](src/pncp/tipos.py): Container personalizado semelhante a lista, com suporte a filtragem e iteração.
-   [`ModeloBasico`](src/pncp/tipos.py): Classe base para modelos Pydantic, garantindo segurança de tipos e validação de dados.
-   **Modelos Pydantic**: Utilizados em todo o projeto para tipagem forte (ex.: `InstrumentoConvocatorio`, `Orgao`, `Resultado`).

## API PNCP

A biblioteca interage diretamente com os endpoints da API do PNCP para buscar filtros e resultados. Todas as requisições são feitas via HTTP utilizando as funções utilitárias [`get_one`](src/pncp/utils.py:13) e [`get_many`](src/pncp/utils.py:6).

## Informações Adicionais

-   Todos os modelos e listas são tipados, utilizando Pydantic para validação.
-   A biblioteca foi projetada para ser extensível e pode ser adaptada para outros endpoints da API PNCP.
-   Para mais detalhes, revise os arquivos fonte em [`src/pncp/instrumentos_convocatorios`](src/pncp/instrumentos_convocatorios/).