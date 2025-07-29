from unittest.mock import patch

import pytest

from pncp.instrumentos_convocatorios.busca import Busca
from pncp.instrumentos_convocatorios.tipos import (
    Ano,
    CamposDeBusca,
    Esfera,
    FonteOrcamentaria,
    InstrumentoConvocatorio,
    ModalidadeDeContratacao,
    Municipio,
    Orgao,
    Poder,
    Resultado,
    Status,
    Unidade,
    UnidadeDaFederacao,
)
from pncp.tipos import Lista


@pytest.fixture
def busca():
    return Busca()


def mock_filtros():
    return {
        "filters": {
            "tipos": [{"id": 1, "nome": "Tipo1", "total": 10}],
            "modalidades": [{"id": 2, "nome": "Modalidade1", "total": 5}],
            "orgaos": [{"id": 3, "nome": "Orgao1", "total": 2, "cnpj": "123"}],
            "unidades": [
                {"id": 4, "nome": "Unidade1", "total": 1, "codigo": "U1", "codigo_nome": "U1Nome"}
            ],
            "ufs": [{"id": 5, "total": 1}],
            "municipios": [{"id": 6, "nome": "Municipio1", "total": 1}],
            "esferas": [{"id": 7, "nome": "Esfera1", "total": 1}],
            "poderes": [{"id": 8, "nome": "Poder1", "total": 1}],
            "anos": [{"ano": 2024, "total": 1}],
            "fontes_orcamentarias": [{"id": 9, "nome": "Fonte1", "total": 1}],
        }
    }


def mock_resultados():
    return {
        "items": [
            {
                "id": 10,
                "index": "idx",
                "doc_type": "type",
                "title": "Titulo",
                "description": "Desc",
                "item_url": "url",
                "document_type": "type",
                "created_at": "2024-01-01T00:00:00",
                "numero": None,
                "ano": "2024",
                "numero_sequencial": "001",
                "numero_sequencial_compra_ata": None,
                "numero_controle_pncp": "NC1",
                "orgao_id": "3",
                "orgao_cnpj": "123",
                "orgao_nome": "Orgao1",
                "orgao_subrogado_id": None,
                "orgao_subrogado_nome": None,
                "unidade_id": "4",
                "unidade_codigo": "U1",
                "unidade_nome": "Unidade1",
                "esfera_id": "7",
                "esfera_nome": "Esfera1",
                "poder_id": "8",
                "poder_nome": "Poder1",
                "municipio_id": "6",
                "municipio_nome": "Municipio1",
                "uf": "5",
                "modalidade_licitacao_id": "2",
                "modalidade_licitacao_nome": "Modalidade1",
                "situacao_id": "todos",
                "situacao_nome": "Todos",
                "data_publicacao_pncp": "2024-01-01T00:00:00",
                "data_atualizacao_pncp": "2024-01-01T00:00:00",
                "data_assinatura": None,
                "data_inicio_vigencia": "2024-01-01T00:00:00",
                "data_fim_vigencia": "2024-01-01T00:00:00",
                "cancelado": False,
                "valor_global": None,
                "tem_resultado": True,
                "tipo_id": "1",
                "tipo_nome": "Tipo1",
                "tipo_contrato_nome": None,
                "fonte_orcamentaria": None,
                "fonte_orcamentaria_id": "9",
                "fonte_orcamentaria_nome": "Fonte1",
            }
        ]
    }


# --- Private Helpers ---


def test_carregar_filtros_caching(busca):
    with patch("pncp.utils.get_one", return_value=mock_filtros()) as mock_get_one:
        busca._carregar_filtros()
        assert busca._filtros is not None
        busca._carregar_filtros()
        mock_get_one.assert_called_once()


def test_verificar_se_existem_resultados_none(busca):
    busca._resultados = None
    busca._verificar_se_existem_resultados()  # Should not raise


def test_verificar_se_existem_resultados_after_search(busca):
    busca._resultados = Lista()
    with pytest.raises(ValueError):
        busca._verificar_se_existem_resultados()


# --- Filter-Listing Methods ---


@pytest.mark.parametrize(
    "method,key,model",
    [
        ("listar_instrumentos_convocatorios", "tipos", InstrumentoConvocatorio),
        ("listar_modalidades_de_contratacao", "modalidades", ModalidadeDeContratacao),
        ("listar_orgaos", "orgaos", Orgao),
        ("listar_unidades", "unidades", Unidade),
        ("listar_ufs", "ufs", UnidadeDaFederacao),
        ("listar_municipios", "municipios", Municipio),
        ("listar_esferas", "esferas", Esfera),
        ("listar_poderes", "poderes", Poder),
        ("listar_anos", "anos", Ano),
        ("listar_fontes_orcamentarias", "fontes_orcamentarias", FonteOrcamentaria),
    ],
)
def test_listar_methods_return_models(busca, method, key, model):
    with patch("pncp.utils.get_one", return_value=mock_filtros()):
        result = getattr(busca, method)()
        assert isinstance(result, Lista)
        assert all(isinstance(x, model) for x in result)


def test_listar_methods_empty(busca):
    with patch("pncp.utils.get_one", return_value={"filters": {}}):
        assert busca.listar_instrumentos_convocatorios() == Lista()
        assert busca.listar_modalidades_de_contratacao() == Lista()


# --- Property Getters ---


def test_property_defaults(busca):
    campos = CamposDeBusca()
    assert busca.texto == campos.q
    assert busca.pagina == campos.pagina
    assert busca.tam_pagina == campos.tam_pagina
    assert busca.status.id == campos.status


def test_status_getter_valid(busca):
    busca._campos_de_busca.status = "em_andamento"
    status = busca.status
    assert isinstance(status, Status)
    assert status.id == "em_andamento"


def test_collection_getters(busca):
    with patch("pncp.utils.get_one", return_value=mock_filtros()):
        busca._campos_de_busca.tipos = Lista([1])
        assert busca.instrumentos_convocatorios[0].id == 1
        busca._campos_de_busca.modalidades = Lista([2])
        assert busca.modalidades_de_contratacao[0].id == 2
        busca._campos_de_busca.orgaos = Lista([3])
        assert busca.orgaos[0].id == 3
        busca._campos_de_busca.unidades = Lista([4])
        assert busca.unidades[0].id == 4
        busca._campos_de_busca.ufs = Lista([5])
        assert busca.ufs[0].id == 5
        busca._campos_de_busca.municipios = Lista([6])
        assert busca.municipios[0].id == 6
        busca._campos_de_busca.esferas = Lista([7])
        assert busca.esferas[0].id == 7
        busca._campos_de_busca.poderes = Lista([8])
        assert busca.poderes[0].id == 8
        busca._campos_de_busca.anos = Lista([2024])
        assert busca.anos[0].ano == 2024
        busca._campos_de_busca.fontes_orcamentarias = Lista([9])
        assert busca.fontes_orcamentarias[0].id == 9


# --- resultados property / buscar() ---


def test_resultados_caching(busca):
    with patch("pncp.utils.get_one", return_value=mock_resultados()) as mock_get_one:
        busca._resultados = None
        result1 = busca.resultados
        assert isinstance(result1, Lista)
        assert all(isinstance(x, Resultado) for x in result1)
        result2 = busca.resultados
        assert result2 is result1
        mock_get_one.assert_called_once()


def test_buscar_returns_resultados(busca):
    with patch("pncp.utils.get_one", return_value=mock_resultados()):
        busca._resultados = None
        result = busca.buscar()
        assert isinstance(result, Lista)
        assert all(isinstance(x, Resultado) for x in result)


# --- Setters for fields and collections ---


def test_setters_update_campos_de_busca(busca):
    busca._resultados = None
    busca.texto = "abc"
    assert busca._campos_de_busca.q == "abc"
    busca.pagina = 2
    assert busca._campos_de_busca.pagina == 2
    busca.tam_pagina = 100
    assert busca._campos_de_busca.tam_pagina == 100


def test_setters_raise_after_search(busca):
    busca._resultados = Lista()
    with pytest.raises(ValueError):
        busca.texto = "abc"
    with pytest.raises(ValueError):
        busca.pagina = 2
    with pytest.raises(ValueError):
        busca.tam_pagina = 100


def test_status_setter_accepts_status_and_id(busca):
    busca._resultados = None
    busca.status = "em_andamento"
    assert busca._campos_de_busca.status == "em_andamento"
    busca.status = Status(id="cancelado", nome="Cancelado")
    assert busca._campos_de_busca.status == "cancelado"


def test_status_setter_invalid_id(busca):
    busca._resultados = None
    with pytest.raises(ValueError):
        busca.status = "invalid"


def test_collection_setters_accept_ids_and_models(busca):
    busca._resultados = None
    busca.instrumentos_convocatorios = [1, InstrumentoConvocatorio(id=2, nome="Tipo2", total=1)]
    assert busca._campos_de_busca.tipos == Lista([1, 2])
    busca.modalidades_de_contratacao = [2, ModalidadeDeContratacao(id=3, nome="Mod2", total=1)]
    assert busca._campos_de_busca.modalidades == Lista([2, 3])
    busca.orgaos = [3, Orgao(id=4, nome="Org2", total=1, cnpj="456")]
    assert busca._campos_de_busca.orgaos == Lista([3, 4])
    busca.unidades = [Unidade(id=5, nome="Unid2", total=1, codigo="U2", codigo_nome="U2Nome"), 6]
    assert busca._campos_de_busca.unidades == Lista([5, 6])
    busca.ufs = [UnidadeDaFederacao(id=7, total=1), 8]
    assert busca._campos_de_busca.ufs == Lista([7, 8])
    busca.municipios = [Municipio(id=9, nome="Mun2", total=1), 10]
    assert busca._campos_de_busca.municipios == Lista([9, 10])
    busca.esferas = [Esfera(id=11, nome="Esf2", total=1), 12]
    assert busca._campos_de_busca.esferas == Lista([11, 12])
    busca.poderes = [Poder(id=13, nome="Pod2", total=1), 14]
    assert busca._campos_de_busca.poderes == Lista([13, 14])
    busca.anos = [Ano(ano=2025, total=1), 2026]
    assert busca._campos_de_busca.anos == Lista([2025, 2026])
    busca.fontes_orcamentarias = [FonteOrcamentaria(id=15, nome="Fonte2", total=1), 16]
    assert busca._campos_de_busca.fontes_orcamentarias == Lista([15, 16])


def test_collection_setters_raise_after_search(busca):
    busca._resultados = Lista()
    with pytest.raises(ValueError):
        busca.instrumentos_convocatorios = [1]
    with pytest.raises(ValueError):
        busca.modalidades_de_contratacao = [2]
    with pytest.raises(ValueError):
        busca.orgaos = [3]
    with pytest.raises(ValueError):
        busca.ufs = [5]
    with pytest.raises(ValueError):
        busca.municipios = [6]
    with pytest.raises(ValueError):
        busca.esferas = [7]
    with pytest.raises(ValueError):
        busca.poderes = [8]
    with pytest.raises(ValueError):
        busca.anos = [2024]
    with pytest.raises(ValueError):
        busca.fontes_orcamentarias = [9]


# --- Convenience preencher_* methods ---


def test_preencher_methods(busca):
    busca._resultados = None
    busca.preencher_texto("abc")
    assert busca._campos_de_busca.q == "abc"
    busca.preencher_pagina(2)
    assert busca._campos_de_busca.pagina == 2
    busca.preencher_tam_pagina(100)
    assert busca._campos_de_busca.tam_pagina == 100
    busca.preencher_status("em_andamento")
    assert busca._campos_de_busca.status == "em_andamento"
    busca.preencher_instrumentos_convocatorios([1])
    assert busca._campos_de_busca.tipos == Lista([1])
    busca.preencher_modalidades_de_contratacao([2])
    assert busca._campos_de_busca.modalidades == Lista([2])
    busca.preencher_orgaos([3])
    assert busca._campos_de_busca.orgaos == Lista([3])
    busca.preencher_unidades([4])
    assert busca._campos_de_busca.unidades == Lista([4])
    busca.preencher_ufs([5])
    assert busca._campos_de_busca.ufs == Lista([5])
    busca.preencher_municipios([6])
    assert busca._campos_de_busca.municipios == Lista([6])
    busca.preencher_esferas([7])
    assert busca._campos_de_busca.esferas == Lista([7])
    busca.preencher_poderes([8])
    assert busca._campos_de_busca.poderes == Lista([8])
    busca.preencher_anos([2024])
    assert busca._campos_de_busca.anos == Lista([2024])
    busca.preencher_fontes_orcamentarias([9])
    assert busca._campos_de_busca.fontes_orcamentarias == Lista([9])


# --- preencher() bulk assign ---


def test_preencher_bulk_assign(busca):
    busca._resultados = None
    busca.preencher(texto="abc", pagina=2, tam_pagina=100, status="em_andamento")
    assert busca._campos_de_busca.q == "abc"
    assert busca._campos_de_busca.pagina == 2
    assert busca._campos_de_busca.tam_pagina == 100
    assert busca._campos_de_busca.status == "em_andamento"


def test_preencher_bulk_assign_none_ignored(busca):
    busca._resultados = None
    busca.preencher(texto=None, pagina=2)
    assert busca._campos_de_busca.q == ""
    assert busca._campos_de_busca.pagina == 2


def test_preencher_bulk_assign_raises_after_search(busca):
    busca._resultados = Lista()
    with pytest.raises(ValueError):
        busca.preencher(texto="abc")


# --- Additional coverage tests ---


def test_listar_status_returns_status_list(busca):
    result = busca.listar_status()
    assert isinstance(result, Lista)
    assert all(isinstance(x, Status) for x in result)


def test_listar_empty_filters_all_methods(busca):
    with patch("pncp.utils.get_one", return_value={"filters": {}}):
        methods = [
            busca.listar_instrumentos_convocatorios,
            busca.listar_modalidades_de_contratacao,
            busca.listar_orgaos,
            busca.listar_unidades,
            busca.listar_ufs,
            busca.listar_municipios,
            busca.listar_esferas,
            busca.listar_poderes,
            busca.listar_anos,
            busca.listar_fontes_orcamentarias,
        ]
        for method in methods:
            assert method() == Lista()


def test_buscar_caching_get_one(busca):
    with patch("pncp.utils.get_one", return_value=mock_resultados()) as mock_get_one:
        busca._resultados = None
        result1 = busca.buscar()
        result2 = busca.buscar()
        assert result2 is result1
        mock_get_one.assert_called_once()


def mock_contratacao():
    return {
        "valor_total_estimado": 1000.0,
        "valor_total_homologado": 900.0,
        "orcamento_sigiloso_codigo": 1,
        "orcamento_sigiloso_descricao": "Sigiloso",
        "numero_controle_PNCP": "NC1",
        "link_sistema_origem": None,
        "link_processo_eletronico": None,
        "ano_compra": 2024,
        "sequencial_compra": 1,
        "numero_compra": "001",
        "processo": "PROC1",
        "orgao_entidade": {
            "cnpj": "123",
            "razao_social": "Orgao1",
            "poder_id": "8",
            "esfera_id": "7",
        },
        "unidade_orgao": {
            "uf_nome": "UF",
            "codigo_ibge": "000",
            "codigo_unidade": "U1",
            "nome_unidade": "Unidade1",
            "uf_sigla": "UF",
            "municipio_nome": "Municipio1",
        },
        "orgao_sub_rogado": None,
        "unidade_sub_rogada": None,
        "modalidade_id": 2,
        "modalidade_nome": "Modalidade1",
        "justificativa_presencial": None,
        "modo_disputa_id": 1,
        "modo_disputa_nome": "Disputa",
        "tipo_instrumento_convocatorio_codigo": 1,
        "tipo_instrumento_convocatorio_nome": "Tipo1",
        "amparo_legal": {
            "descricao": "Legal",
            "nome": "Amparo",
            "codigo": 1,
        },
        "objeto_compra": "Objeto",
        "informacao_complementar": "Info",
        "srp": False,
        "fontes_orcamentarias": [],
        "data_publicacao_pncp": "2024-01-01T00:00:00",
        "data_abertura_proposta": "2024-01-01T00:00:00",
        "data_encerramento_proposta": "2024-01-01T00:00:00",
        "situacao_compra_id": 1,
        "situacao_compra_nome": "Em andamento",
        "existe_resultado": True,
        "data_inclusao": "2024-01-01T00:00:00",
        "data_atualizacao": "2024-01-01T00:00:00",
        "data_atualizacao_global": "2024-01-01T00:00:00",
        "usuario_nome": "User",
    }


def mock_itens():
    return [
        {
            "numero_item": 1,
            "descricao": "Item 1",
            "material_ou_servico": "Material",
            "material_ou_servico_nome": "Material Nome",
            "valor_unitario_estimado": 100.0,
            "valor_total": 200.0,
            "quantidade": 2,
            "unidade_medida": "UN",
            "orcamento_sigiloso": False,
            "item_categoria_id": 1,
            "item_categoria_nome": "Categoria",
            "patrimonio": None,
            "codigo_registro_imobiliario": None,
            "criterio_julgamento_id": 1,
            "criterio_julgamento_nome": "Menor preço",
            "situacao_compra_item": 1,
            "situacao_compra_item_nome": "Em andamento",
            "tipo_beneficio": 1,
            "tipo_beneficio_nome": "Nenhum",
            "incentivo_produtivo_basico": False,
            "data_inclusao": "2024-01-01T00:00:00",
            "data_atualizacao": "2024-01-01T00:00:00",
            "tem_resultado": True,
            "imagem": 0,
            "aplicabilidade_margem_preferencia_normal": False,
            "aplicabilidade_margem_preferencia_adicional": False,
            "percentual_margem_preferencia_normal": None,
            "percentual_margem_preferencia_adicional": None,
            "ncm_nbs_codigo": None,
            "ncm_nbs_descricao": None,
            "catalogo": None,
            "categoria_item_catalogo": None,
            "catalogo_codigo_item": None,
            "informacao_complementar": None,
        }
    ]


def test_resultado_detalhar_listar_itens_integration():
    def get_one_side_effect(url, *args, **kwargs):
        if "filters" in url:
            return mock_filtros()
        if "search" in url:
            return mock_resultados()
        return {}

    class MockResponse:
        def json(self):
            return mock_contratacao()

        def raise_for_status(self):
            pass

    with (
        patch("pncp.utils.get_one", side_effect=get_one_side_effect),
        patch("pncp.instrumentos_convocatorios.tipos.get_many", return_value=mock_itens()),
        patch("httpx.Client.get", return_value=MockResponse()),
    ):
        busca = Busca()
        busca.preencher(orgaos=[3], instrumentos_convocatorios=[1], anos=[2024])
        resultados = busca.resultados
        assert isinstance(resultados, Lista)
        assert resultados
        resultado = resultados[0]
        contratacao = resultado.detalhar()
        itens = contratacao.listar_itens()
        assert hasattr(contratacao, "listar_itens")
        assert isinstance(itens, Lista)
        assert len(itens) == 1
        item = itens[0]
        assert item.numero_item == 1
        assert item.descricao == "Item 1"
        assert item.valor_unitario_estimado == 100.0
        assert item.valor_total == 200.0
        assert item.quantidade == 2


def test_fluxo_scratchpad():
    from pncp.tipos import Lista

    class MockResponse:
        def json(self):
            return mock_contratacao()

        def raise_for_status(self):
            pass

    with (
        patch(
            "pncp.utils.get_one",
            side_effect=[mock_filtros(), mock_resultados()],
        ),
        patch("pncp.instrumentos_convocatorios.tipos.get_many", return_value=mock_itens()),
        patch("httpx.Client.get", return_value=MockResponse()),
    ):
        busca = Busca()
        camara_dos_deputados = busca.listar_orgaos().filtrar(lambda o: "orgao1" in o.nome.lower())
        aviso_de_dispensa = busca.listar_instrumentos_convocatorios().filtrar(
            lambda i: "tipo1" in i.nome.lower()
        )
        busca.preencher(
            orgaos=camara_dos_deputados, instrumentos_convocatorios=aviso_de_dispensa, anos=[2024]
        )
        resultados = busca.resultados
        assert isinstance(resultados, Lista)
        assert resultados
        resultado = resultados[0]
        contratacao = resultado.detalhar()
        itens = contratacao.listar_itens()
        assert isinstance(itens, Lista)
        assert len(itens) == 1
        item = itens[0]
        assert item.numero_item == 1
        assert item.descricao == "Item 1"
