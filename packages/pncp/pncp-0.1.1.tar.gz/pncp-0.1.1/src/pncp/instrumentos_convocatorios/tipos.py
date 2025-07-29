from datetime import datetime
from typing import Literal, Self

from pncp.tipos import Lista, ModeloBasico
from pncp.utils import get_many, get_one

type Id = str | int


class Status(ModeloBasico):
    id: Id
    nome: str

    @classmethod
    def listar(cls) -> Lista[Self]:
        return Lista(
            [
                cls(id="todos", nome="Todos"),
                cls(id="em_andamento", nome="Em Andamento"),
                cls(id="concluido", nome="Concluído"),
                cls(id="cancelado", nome="Cancelado"),
            ]
        )


class InstrumentoConvocatorio(ModeloBasico):
    id: Id
    nome: str
    total: int


class ModalidadeDeContratacao(ModeloBasico):
    id: Id
    nome: str
    total: int


class Orgao(ModeloBasico):
    id: Id
    nome: str
    total: int
    cnpj: str


class Unidade(ModeloBasico):
    id: Id
    nome: str
    total: int
    codigo: str
    codigo_nome: str


class UnidadeDaFederacao(ModeloBasico):
    id: Id
    total: int


class Municipio(ModeloBasico):
    id: Id
    nome: str
    total: int


class Esfera(ModeloBasico):
    id: Id
    nome: str
    total: int


class Poder(ModeloBasico):
    id: Id
    nome: str
    total: int


class Ano(ModeloBasico):
    ano: Id
    total: int


class FonteOrcamentaria(ModeloBasico):
    id: Id
    nome: str
    total: int


class CamposDeBusca(ModeloBasico):
    tipos_documento: Literal["edital"] = "edital"

    q: str = ""
    pagina: int = 1
    tam_pagina: int = 500
    status: Id = "todos"
    tipos: Lista[Id] = Lista()
    orgaos: Lista[Id] = Lista()
    unidades: Lista[Id] = Lista()
    esferas: Lista[Id] = Lista()
    poderes: Lista[Id] = Lista()
    ufs: Lista[Id] = Lista()
    municipios: Lista[Id] = Lista()
    modalidades: Lista[Id] = Lista()
    anos: Lista[Id] = Lista()
    fontes_orcamentarias: Lista[Id] = Lista()


class Resultado(ModeloBasico):
    id: Id
    index: str
    doc_type: str
    title: str
    description: str
    item_url: str
    document_type: str
    created_at: datetime
    numero: str | None
    ano: str
    numero_sequencial: str
    numero_sequencial_compra_ata: str | None
    numero_controle_pncp: str
    orgao_id: str
    orgao_cnpj: str
    orgao_nome: str
    orgao_subrogado_id: str | None
    orgao_subrogado_nome: str | None
    unidade_id: str
    unidade_codigo: str
    unidade_nome: str
    esfera_id: str
    esfera_nome: str
    poder_id: str
    poder_nome: str
    municipio_id: str
    municipio_nome: str
    uf: str
    modalidade_licitacao_id: str
    modalidade_licitacao_nome: str
    situacao_id: str
    situacao_nome: str
    data_publicacao_pncp: datetime
    data_atualizacao_pncp: datetime
    data_assinatura: datetime | None
    data_inicio_vigencia: datetime
    data_fim_vigencia: datetime
    cancelado: bool
    valor_global: float | None
    tem_resultado: bool
    tipo_id: str
    tipo_nome: str
    tipo_contrato_nome: str | None
    fonte_orcamentaria: str | None
    fonte_orcamentaria_id: str | None
    fonte_orcamentaria_nome: str | None

    def detalhar(self) -> "Contratacao":
        url = f"https://pncp.gov.br/api/consulta/v1/orgaos/{self.orgao_cnpj}/compras/{self.ano}/{self.numero_sequencial}"
        data = get_one(url)
        return Contratacao(**data)


class IOrgaoEntidade(ModeloBasico):
    cnpj: str
    razao_social: str
    poder_id: str
    esfera_id: str


class IUnidadeOrgao(ModeloBasico):
    uf_nome: str
    codigo_ibge: str
    codigo_unidade: str
    nome_unidade: str
    uf_sigla: str
    municipio_nome: str


class IOrgaoSubRogado(ModeloBasico):
    cnpj: str
    razao_social: str
    poder_id: str
    esfera_id: str


class IUnidadeSubRogada(ModeloBasico):
    uf_nome: str
    codigo_ibge: str
    codigo_unidade: str
    nome_unidade: str
    uf_sigla: str
    municipio_nome: str


class IAmparoLegal(ModeloBasico):
    descricao: str
    nome: str
    codigo: int


class IFonteOrcamentaria(ModeloBasico):
    codigo: int
    nome: str
    descricao: str
    data_inclusao: datetime


class Contratacao(ModeloBasico):
    valor_total_estimado: float
    valor_total_homologado: float | None
    orcamento_sigiloso_codigo: int
    orcamento_sigiloso_descricao: str
    numero_controle_PNCP: str
    link_sistema_origem: str | None
    link_processo_eletronico: str | None
    ano_compra: int
    sequencial_compra: int
    numero_compra: str
    processo: str
    orgao_entidade: IOrgaoEntidade
    unidade_orgao: IUnidadeOrgao
    orgao_sub_rogado: IOrgaoSubRogado | None
    unidade_sub_rogada: IUnidadeSubRogada | None
    modalidade_id: int
    modalidade_nome: str
    justificativa_presencial: str | None
    modo_disputa_id: int
    modo_disputa_nome: str
    tipo_instrumento_convocatorio_codigo: int
    tipo_instrumento_convocatorio_nome: str
    amparo_legal: IAmparoLegal
    objeto_compra: str
    informacao_complementar: str | None
    srp: bool
    fontes_orcamentarias: list[IFonteOrcamentaria]  # TODO: Converter para Lista
    data_publicacao_pncp: datetime
    data_abertura_proposta: datetime
    data_encerramento_proposta: datetime
    situacao_compra_id: int
    situacao_compra_nome: str
    existe_resultado: bool
    data_inclusao: datetime
    data_atualizacao: datetime
    data_atualizacao_global: datetime
    usuario_nome: str

    def listar_itens(self) -> Lista["Item"]:
        url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{self.orgao_entidade.cnpj}/compras/{self.ano_compra}/{self.sequencial_compra}/itens"
        params = {
            "pagina": 1,
            "tamanhoPagina": 500,
        }
        data = get_many(url, params=params)
        return Lista([Item(**item) for item in data])

    def listar_documentos(self) -> None:
        raise NotImplementedError("Método não implementado")

    def obter_historico(self) -> None:
        raise NotImplementedError("Método não implementado")


class ICatalogo(ModeloBasico):
    id: int
    nome: str
    descricao: str
    data_inclusao: datetime
    data_atualizacao: datetime
    status_ativo: bool
    url: str


class ICategoriaItemCatalogo(ModeloBasico):
    id: int
    nome: str
    descricao: str
    data_inclusao: datetime
    data_atualizacao: datetime
    status_ativo: bool


class Item(ModeloBasico):
    numero_item: int
    descricao: str
    material_ou_servico: str
    material_ou_servico_nome: str
    valor_unitario_estimado: float
    valor_total: float
    quantidade: float
    unidade_medida: str
    orcamento_sigiloso: bool
    item_categoria_id: int
    item_categoria_nome: str
    patrimonio: str | None
    codigo_registro_imobiliario: str | None
    criterio_julgamento_id: int
    criterio_julgamento_nome: str
    situacao_compra_item: int
    situacao_compra_item_nome: str
    tipo_beneficio: int
    tipo_beneficio_nome: str
    incentivo_produtivo_basico: bool
    data_inclusao: datetime
    data_atualizacao: datetime
    tem_resultado: bool
    imagem: int
    aplicabilidade_margem_preferencia_normal: bool
    aplicabilidade_margem_preferencia_adicional: bool
    percentual_margem_preferencia_normal: float | None
    percentual_margem_preferencia_adicional: float | None
    ncm_nbs_codigo: str | None
    ncm_nbs_descricao: str | None
    catalogo: ICatalogo | None
    categoria_item_catalogo: ICategoriaItemCatalogo | None
    catalogo_codigo_item: str | None
    informacao_complementar: str | None

    def listar_resultados(self) -> None:
        raise NotImplementedError("Método não implementado")

    def listar_imagens(self) -> None:
        raise NotImplementedError("Método não implementado")
