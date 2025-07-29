from pprint import pprint

from pncp.instrumentos_convocatorios import Busca

try:
    busca = Busca()

    camara_dos_deputados = busca.listar_orgaos().filtrar(
        lambda orgao: orgao.nome == "Câmara dos Deputados"
    )

    aviso_de_dispensa = busca.listar_instrumentos_convocatorios().filtrar(
        lambda instrumento: ("aviso" in instrumento.nome.lower())
    )

    busca.preencher(
        orgaos=camara_dos_deputados,
        instrumentos_convocatorios=aviso_de_dispensa,
        anos=[2025],
    )

    if busca.resultados:
        ultima_dispensa = busca.resultados[-1]
        ultima_dispensa_detalhada = ultima_dispensa.detalhar()
        itens = ultima_dispensa_detalhada.listar_itens()

        for item in itens:
            pprint(item)
except Exception as e:
    print(f"Erro: {type(e).__name__}: {e}")
