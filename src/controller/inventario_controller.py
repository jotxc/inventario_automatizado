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
        self.ultimos_parametros = None

    def carregar(self):
        self.estoque = preparar_inventario()
        self.descricao_excluir = set()
        self.sugestao_base = None
        self.ultimo_resultado = None
        self.ultimos_parametros = None

        tipos = (
            self.estoque["tipo_deposito"]
            .drop_duplicates()
            .sort_values()
            .apply(lambda v: str(int(float(str(v)))))
            .tolist()
        )

        return tipos

    def obter_visao_geral(self):
        if self.estoque is None or self.estoque.empty:
            return None

        from historico.historico_documentos import carregar_historico_documentos, remover_lotes_historico
        from integracoes.sugestao import criar_sugestao_inventario, identificar_primeira_contagem

        dados = self.estoque.copy()
        sugestao = criar_sugestao_inventario(dados)
        sugestao = identificar_primeira_contagem(sugestao)

        historico = carregar_historico_documentos()
        sugestao = remover_lotes_historico(sugestao, historico)

        visao = sugestao.groupby("tipo_deposito").agg(
            total_lotes=("lote", "count"),
            total_posicoes=("quantidade_posicoes", "sum"),
            valor_pendente=("valor_lote", "sum"),
            lotes_nunca_contados=("nunca_contado", "sum"),
            media_dias_sem_contagem=("dias_sem_contagem", "mean"),
            max_dias_sem_contagem=("dias_sem_contagem", "max"),
        ).reset_index()

        visao["percentual_primeira_contagem"] = (
            visao["lotes_nunca_contados"] / visao["total_lotes"] * 100
        ).round(1)

        valor_nunca = (
            sugestao[sugestao["nunca_contado"]]
            .groupby("tipo_deposito")["valor_lote"]
            .sum()
        )
        visao["valor_pendente_primeira_contagem"] = (
            visao["tipo_deposito"].map(valor_nunca).fillna(0)
        )

        return visao

    def _excluir_descricoes(self, dataframe):
        if not self.descricao_excluir or dataframe is None or dataframe.empty:
            return dataframe
        return dataframe[
            ~dataframe["descricao_material"].isin(self.descricao_excluir)
        ]

    def parametros_iguais_ultima_geracao(self, parametros):
        if self.ultimos_parametros is None:
            return False
        return self.ultimos_parametros == parametros

    def gerar(
        self,
        criterio,
        tipo_deposito,
        limite_posicoes,
        modo_sem_maquina=True,
        criterio_secundario=None,
        baixas_por_ultimo=False
    ):
        self.ultimos_parametros = {
            "criterio": criterio,
            "criterio_secundario": criterio_secundario,
            "tipo_deposito": tipo_deposito,
            "limite_posicoes": limite_posicoes,
            "modo_sem_maquina": modo_sem_maquina,
            "baixas_por_ultimo": baixas_por_ultimo,
        }

        resultado = executar_inventario(
            estoque=self.estoque,
            criterio=criterio,
            tipo_deposito=tipo_deposito,
            limite_posicoes=limite_posicoes,
            modo_sem_maquina=modo_sem_maquina,
            criterio_secundario=criterio_secundario,
            descricao_excluir=self.descricao_excluir,
            baixas_por_ultimo=baixas_por_ultimo
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
