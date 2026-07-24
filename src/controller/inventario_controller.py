from core.inventario import (
    preparar_inventario,
    executar_inventario
)
from regras.filtros import filtrar_tipo_deposito
from regras.bloqueios import remover_lotes_acima_nivel_1
from integracoes.sugestao import criar_sugestao_inventario, identificar_primeira_contagem
from regras.priorizacao import priorizar_lotes, priorizar_combinado
from regras.selecao import selecionar_lotes
from historico.historico_documentos import carregar_historico_documentos, remover_lotes_historico


class InventarioController:

    def __init__(self):
        self.estoque = None
        self.sugestao_base = None
        self.descricao_excluir = set()
        self.ultimo_resultado = None

    def carregar(self):
        self.estoque = preparar_inventario()
        self.descricao_excluir = set()
        self.sugestao_base = None
        self.ultimo_resultado = None

        tipos = (
            self.estoque["tipo_deposito"]
            .drop_duplicates()
            .sort_values()
            .astype(str)
            .tolist()
        )

        return tipos

    def _excluir_descricoes(self, dataframe):
        if not self.descricao_excluir or dataframe is None or dataframe.empty:
            return dataframe
        return dataframe[
            ~dataframe["descricao_material"].isin(self.descricao_excluir)
        ]

    def gerar(
        self,
        criterio,
        tipo_deposito,
        limite_posicoes,
        modo_sem_maquina=True,
        criterio_secundario=None
    ):
        resultado = executar_inventario(
            estoque=self.estoque,
            criterio=criterio,
            tipo_deposito=tipo_deposito,
            limite_posicoes=limite_posicoes,
            modo_sem_maquina=modo_sem_maquina,
            criterio_secundario=criterio_secundario,
            descricao_excluir=self.descricao_excluir
        )

        self.ultimo_resultado = resultado
        return resultado

    def consultar_estoque(
        self,
        criterio,
        tipo_deposito,
        limite_posicoes,
        modo_sem_maquina=True,
        criterio_secundario=None
    ):
        dados = self.estoque.copy()
        dados = filtrar_tipo_deposito(dados, tipo_deposito)

        if modo_sem_maquina:
            dados = remover_lotes_acima_nivel_1(dados)

        sugestao = criar_sugestao_inventario(dados)

        sugestao = identificar_primeira_contagem(sugestao)

        historico = carregar_historico_documentos()
        sugestao = remover_lotes_historico(sugestao, historico)

        self.sugestao_base = sugestao.copy()

        sugestao = self._excluir_descricoes(sugestao)

        if criterio == "primeira_contagem" or criterio_secundario == "primeira_contagem":
            sugestao = sugestao[sugestao["nunca_contado"] == True]

        if criterio_secundario:
            sugestao = priorizar_combinado(sugestao, criterio, criterio_secundario)
        else:
            sugestao = priorizar_lotes(sugestao, criterio=criterio)

        sugestao = selecionar_lotes(sugestao, limite_posicoes=limite_posicoes)

        return sugestao
