from typing import Iterable

import pncp.utils
from pncp.tipos import Lista

from .tipos import (
    Ano,
    CamposDeBusca,
    Esfera,
    FonteOrcamentaria,
    Id,
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


class Busca:
    _url_filtros = "https://pncp.gov.br/api/search/filters?tipos_documento=edital"
    _url_busca = "https://pncp.gov.br/api/search"

    def __init__(self):
        self._filtros = None
        self._campos_de_busca = CamposDeBusca()
        self._resultados: Lista[Resultado] | None = None

    def _carregar_filtros(self):
        if self._filtros is None:
            data = pncp.utils.get_one(self._url_filtros)
            self._filtros = data["filters"]

    def _verificar_se_existem_resultados(self) -> None:
        if self._resultados is not None:
            raise ValueError("Não é possível modificar uma busca já realizada.")

    def listar_status(self) -> Lista[Status]:
        return Status.listar()

    def listar_instrumentos_convocatorios(self) -> Lista[InstrumentoConvocatorio]:
        self._carregar_filtros()

        if not self._filtros or "tipos" not in self._filtros:
            return Lista()

        return Lista(
            InstrumentoConvocatorio(**instrumento_convocatorio)
            for instrumento_convocatorio in self._filtros["tipos"]
        )

    def listar_modalidades_de_contratacao(self) -> Lista[ModalidadeDeContratacao]:
        self._carregar_filtros()

        if not self._filtros or "modalidades" not in self._filtros:
            return Lista()

        return Lista(
            ModalidadeDeContratacao(**modalidade_de_contratacao)
            for modalidade_de_contratacao in self._filtros["modalidades"]
        )

    def listar_orgaos(self) -> Lista[Orgao]:
        self._carregar_filtros()

        if not self._filtros or "orgaos" not in self._filtros:
            return Lista()

        return Lista(Orgao(**orgao) for orgao in self._filtros["orgaos"])

    def listar_unidades(self) -> Lista[Unidade]:
        self._carregar_filtros()

        if not self._filtros or "unidades" not in self._filtros:
            return Lista()

        return Lista(Unidade(**unidade) for unidade in self._filtros["unidades"])

    def listar_ufs(self) -> Lista[UnidadeDaFederacao]:
        self._carregar_filtros()

        if not self._filtros or "ufs" not in self._filtros:
            return Lista()

        return Lista(UnidadeDaFederacao(**uf) for uf in self._filtros["ufs"])

    def listar_municipios(self) -> Lista[Municipio]:
        self._carregar_filtros()

        if not self._filtros or "municipios" not in self._filtros:
            return Lista()

        return Lista(Municipio(**municipio) for municipio in self._filtros["municipios"])

    def listar_esferas(self) -> Lista[Esfera]:
        self._carregar_filtros()

        if not self._filtros or "esferas" not in self._filtros:
            return Lista()

        return Lista(Esfera(**esfera) for esfera in self._filtros["esferas"])

    def listar_poderes(self) -> Lista[Poder]:
        self._carregar_filtros()

        if not self._filtros or "poderes" not in self._filtros:
            return Lista()

        return Lista(Poder(**poder) for poder in self._filtros["poderes"])

    def listar_anos(self) -> Lista[Ano]:
        self._carregar_filtros()

        if not self._filtros or "anos" not in self._filtros:
            return Lista()

        return Lista(Ano(**ano) for ano in self._filtros["anos"])

    def listar_fontes_orcamentarias(self) -> Lista[FonteOrcamentaria]:
        self._carregar_filtros()

        if not self._filtros or "fontes_orcamentarias" not in self._filtros:
            return Lista()

        return Lista(
            FonteOrcamentaria(**fonte_orcamentaria)
            for fonte_orcamentaria in self._filtros["fontes_orcamentarias"]
        )

    @property
    def texto(self) -> str:
        return self._campos_de_busca.q

    @property
    def pagina(self) -> int:
        return self._campos_de_busca.pagina

    @property
    def tam_pagina(self) -> int:
        return self._campos_de_busca.tam_pagina

    @property
    def status(self) -> Status:
        return (
            self.listar_status()
            .filtrar(lambda status: status.id == self._campos_de_busca.status)
            .pop()
        )

    @property
    def instrumentos_convocatorios(self) -> Lista[InstrumentoConvocatorio]:
        return Lista(
            instrumento_convocatorio
            for instrumento_convocatorio in self.listar_instrumentos_convocatorios()
            if instrumento_convocatorio.id in self._campos_de_busca.tipos
        )

    @property
    def modalidades_de_contratacao(self) -> Lista[ModalidadeDeContratacao]:
        return Lista(
            modalidade_de_contratacao
            for modalidade_de_contratacao in self.listar_modalidades_de_contratacao()
            if modalidade_de_contratacao.id in self._campos_de_busca.modalidades
        )

    @property
    def orgaos(self) -> Lista[Orgao]:
        return Lista(
            orgao for orgao in self.listar_orgaos() if orgao.id in self._campos_de_busca.orgaos
        )

    @property
    def unidades(self) -> Lista[Unidade]:
        return Lista(
            unidade
            for unidade in self.listar_unidades()
            if unidade.id in self._campos_de_busca.unidades
        )

    @property
    def ufs(self) -> Lista[UnidadeDaFederacao]:
        return Lista(uf for uf in self.listar_ufs() if uf.id in self._campos_de_busca.ufs)

    @property
    def municipios(self) -> Lista[Municipio]:
        return Lista(
            municipio
            for municipio in self.listar_municipios()
            if municipio.id in self._campos_de_busca.municipios
        )

    @property
    def esferas(self) -> Lista[Esfera]:
        return Lista(
            esfera for esfera in self.listar_esferas() if esfera.id in self._campos_de_busca.esferas
        )

    @property
    def poderes(self) -> Lista[Poder]:
        return Lista(
            poder for poder in self.listar_poderes() if poder.id in self._campos_de_busca.poderes
        )

    @property
    def anos(self) -> Lista[Ano]:
        return Lista(ano for ano in self.listar_anos() if ano.ano in self._campos_de_busca.anos)

    @property
    def fontes_orcamentarias(self) -> Lista[FonteOrcamentaria]:
        return Lista(
            fonte_orcamentaria
            for fonte_orcamentaria in self.listar_fontes_orcamentarias()
            if fonte_orcamentaria.id in self._campos_de_busca.fontes_orcamentarias
        )

    @property
    def resultados(self) -> Lista[Resultado]:
        if self._resultados is not None:
            return self._resultados
        data = pncp.utils.get_one(
            self._url_busca,
            params=self._campos_de_busca.como_dicionario(),
        )
        self._resultados = Lista(Resultado(**resultado) for resultado in data["items"])
        return self._resultados

    @texto.setter
    def texto(self, texto: str):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.q = texto

    @pagina.setter
    def pagina(self, pagina: int):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.pagina = pagina

    @tam_pagina.setter
    def tam_pagina(self, tam_pagina: int):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.tam_pagina = tam_pagina

    @status.setter
    def status(self, status: Id | Status):
        self._verificar_se_existem_resultados()

        status_id = status.id if isinstance(status, Status) else status
        valid_ids = [s.id for s in self.listar_status()]
        if status_id not in valid_ids:
            raise ValueError(f"Status inválido: {status}")

        self._campos_de_busca.status = status_id

    @instrumentos_convocatorios.setter
    def instrumentos_convocatorios(
        self, instrumentos_convocatorios: Iterable[Id] | Iterable[InstrumentoConvocatorio]
    ):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.tipos = Lista(
            instrumento.id if isinstance(instrumento, InstrumentoConvocatorio) else instrumento
            for instrumento in instrumentos_convocatorios
        )

    @modalidades_de_contratacao.setter
    def modalidades_de_contratacao(
        self, modalidades_de_contratacao: Iterable[Id] | Iterable[ModalidadeDeContratacao]
    ):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.modalidades = Lista(
            modalidade.id if isinstance(modalidade, ModalidadeDeContratacao) else modalidade
            for modalidade in modalidades_de_contratacao
        )

    @orgaos.setter
    def orgaos(self, orgaos: Iterable[Id] | Iterable[Orgao]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.orgaos = Lista(
            orgao.id if isinstance(orgao, Orgao) else orgao for orgao in orgaos
        )

    @unidades.setter
    def unidades(self, unidades: Iterable[Id] | Iterable[Unidade]):
        self._campos_de_busca.unidades = Lista(
            unidade.id if isinstance(unidade, Unidade) else unidade for unidade in unidades
        )

    @ufs.setter
    def ufs(self, ufs: Iterable[Id] | Iterable[UnidadeDaFederacao]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.ufs = Lista(
            uf.id if isinstance(uf, UnidadeDaFederacao) else uf for uf in ufs
        )

    @municipios.setter
    def municipios(self, municipios: Iterable[Id] | Iterable[Municipio]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.municipios = Lista(
            municipio.id if isinstance(municipio, Municipio) else municipio
            for municipio in municipios
        )

    @esferas.setter
    def esferas(self, esferas: Iterable[Id] | Iterable[Esfera]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.esferas = Lista(
            esfera.id if isinstance(esfera, Esfera) else esfera for esfera in esferas
        )

    @poderes.setter
    def poderes(self, poderes: Iterable[Id] | Iterable[Poder]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.poderes = Lista(
            poder.id if isinstance(poder, Poder) else poder for poder in poderes
        )

    @anos.setter
    def anos(self, anos: Iterable[Id] | Iterable[Ano]):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.anos = Lista(ano.ano if isinstance(ano, Ano) else ano for ano in anos)

    @fontes_orcamentarias.setter
    def fontes_orcamentarias(
        self, fontes_orcamentarias: Iterable[Id] | Iterable[FonteOrcamentaria]
    ):
        self._verificar_se_existem_resultados()
        self._campos_de_busca.fontes_orcamentarias = Lista(
            fonte.id if isinstance(fonte, FonteOrcamentaria) else fonte
            for fonte in fontes_orcamentarias
        )

    def preencher_texto(self, texto: str):
        self.texto = texto

    def preencher_pagina(self, pagina: int):
        self.pagina = pagina

    def preencher_tam_pagina(self, tam_pagina: int):
        self.tam_pagina = tam_pagina

    def preencher_status(self, status: Id | Status):
        self.status = status

    def preencher_instrumentos_convocatorios(
        self, instrumentos_convocatorios: Iterable[Id] | Iterable[InstrumentoConvocatorio]
    ):
        self.instrumentos_convocatorios = instrumentos_convocatorios

    def preencher_modalidades_de_contratacao(
        self, modalidades_de_contratacao: Iterable[Id] | Iterable[ModalidadeDeContratacao]
    ):
        self.modalidades_de_contratacao = modalidades_de_contratacao

    def preencher_orgaos(self, orgaos: Iterable[Id] | Iterable[Orgao]):
        self.orgaos = orgaos

    def preencher_unidades(self, unidades: Iterable[Id] | Iterable[Unidade]):
        self.unidades = unidades

    def preencher_ufs(self, ufs: Iterable[Id] | Iterable[UnidadeDaFederacao]):
        self.ufs = ufs

    def preencher_municipios(self, municipios: Iterable[Id] | Iterable[Municipio]):
        self.municipios = municipios

    def preencher_esferas(self, esferas: Iterable[Id] | Iterable[Esfera]):
        self.esferas = esferas

    def preencher_poderes(self, poderes: Iterable[Id] | Iterable[Poder]):
        self.poderes = poderes

    def preencher_anos(self, anos: Iterable[Id] | Iterable[Ano]):
        self.anos = anos

    def preencher_fontes_orcamentarias(
        self, fontes_orcamentarias: Iterable[Id] | Iterable[FonteOrcamentaria]
    ):
        self.fontes_orcamentarias = fontes_orcamentarias

    def preencher(
        self,
        texto: str | None = None,
        pagina: int | None = None,
        tam_pagina: int | None = None,
        status: Id | Status | None = None,
        instrumentos_convocatorios: Iterable[Id] | Iterable[InstrumentoConvocatorio] | None = None,
        modalidades_de_contratacao: Iterable[Id] | Iterable[ModalidadeDeContratacao] | None = None,
        orgaos: Iterable[Id] | Iterable[Orgao] | None = None,
        unidades: Iterable[Id] | Iterable[Unidade] | None = None,
        ufs: Iterable[Id] | Iterable[UnidadeDaFederacao] | None = None,
        municipios: Iterable[Id] | Iterable[Municipio] | None = None,
        esferas: Iterable[Id] | Iterable[Esfera] | None = None,
        poderes: Iterable[Id] | Iterable[Poder] | None = None,
        anos: Iterable[Id] | Iterable[Ano] | None = None,
        fontes_orcamentarias: Iterable[Id] | Iterable[FonteOrcamentaria] | None = None,
    ):
        kwargs = {k: v for k, v in locals().items() if k != "self" and v is not None}
        for key, value in kwargs.items():
            setattr(self, key, value)

    def buscar(self):
        return self.resultados
