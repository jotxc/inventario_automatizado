from core.inventario import (
    _carregar_base,
    preparar_inventario,
    executar_inventario
)
from regras.filtros import filtrar_tipo_deposito
from regras.bloqueios import (
    remover_lotes_acima_nivel_1,
    remover_lotes_em_ordem,
    remover_posicoes_330_em_ordem
)
from integracoes.sugestao import criar_sugestao_inventario, identificar_primeira_contagem
from regras.priorizacao import priorizar_lotes, priorizar_combinado
from regras.selecao import selecionar_lotes
from historico.historico_documentos import (
    carregar_historico_documentos, remover_lotes_historico, carregar_ultima_geracao,
    atualizar_documento_geracao, listar_geracoes, excluir_geracao, obter_detalhes_geracao
)


class InventarioController:

    def __init__(self):
        self.estoque = None
        self.estoque_visao = None
        self.sugestao_base = None
        self.descricao_excluir = set()
        self.ultimo_resultado = None
        self.ultimos_parametros = None
        self._cache_historico = None

    def _obter_historico(self):
        if self._cache_historico is not None:
            return self._cache_historico
        self._cache_historico = carregar_historico_documentos()
        return self._cache_historico

    def _invalidar_cache_historico(self):
        self._cache_historico = None

    def carregar(self):
        base = _carregar_base()

        self.estoque_visao = base
        self.estoque = base.copy()
        self.estoque = remover_lotes_em_ordem(self.estoque)
        self.estoque = remover_posicoes_330_em_ordem(self.estoque)

        self.descricao_excluir = set()
        self.sugestao_base = None
        self.ultimo_resultado = None
        self.ultimos_parametros = None
        self._invalidar_cache_historico()

        tipos = (
            self.estoque["tipo_deposito"]
            .drop_duplicates()
            .sort_values()
            .apply(lambda v: str(int(float(str(v)))))
            .tolist()
        )

        return tipos

    def obter_visao_geral(self):
        if self.estoque_visao is None or self.estoque_visao.empty:
            return None

        from integracoes.sugestao import criar_sugestao_inventario, identificar_primeira_contagem

        dados = self.estoque_visao.copy()
        print(f"\n[DIAG] 1. Posições no estoque_visao: {len(dados)}")
        print(f"[DIAG] 1a. Lotes únicos no estoque_visao: {dados['lote'].nunique()}")

        sugestao = criar_sugestao_inventario(dados)
        print(f"[DIAG] 2. Linhas na sugestão (material+lote): {len(sugestao)}")
        print(f"[DIAG] 2a. Lotes únicos na sugestão: {sugestao['lote'].nunique()}")

        sugestao = identificar_primeira_contagem(sugestao)

        por_tipo = sugestao.groupby("tipo_deposito").agg(
            total_lotes=("lote", "count"),
            lotes_unicos=("lote", "nunique"),
        ).reset_index()
        print(f"[DIAG] 3. Por tipo_depósito:\n{por_tipo.to_string(index=False)}")
        print(f"[DIAG] 3a. Soma count(lote): {por_tipo['total_lotes'].sum()}")
        print(f"[DIAG] 3b. Soma lotes únicos: {por_tipo['lotes_unicos'].sum()}")

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

    def aplicar_exclusao(self, dataframe):
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
        }

        resultado = executar_inventario(
            estoque=self.estoque,
            criterio=criterio,
            tipo_deposito=tipo_deposito,
            limite_posicoes=limite_posicoes,
            modo_sem_maquina=modo_sem_maquina,
            criterio_secundario=criterio_secundario,
            descricao_excluir=self.descricao_excluir,
            baixas_por_ultimo=baixas_por_ultimo,
            historico=self._obter_historico()
        )

        self._invalidar_cache_historico()
        self.ultimo_resultado = resultado
        return resultado

    def carregar_ultimo_documento_historico(self):
        return carregar_ultima_geracao()

    def atualizar_numero_documento(self, id_geracao, numero_documento):
        sucesso, mensagem = atualizar_documento_geracao(id_geracao, numero_documento)
        self._invalidar_cache_historico()
        return sucesso, mensagem

    def listar_geracoes_historico(self):
        return listar_geracoes()

    def excluir_geracao_historico(self, id_geracao):
        resultado = excluir_geracao(id_geracao)
        self._invalidar_cache_historico()
        return resultado

    def obter_detalhes_geracao(self, id_geracao):
        return obter_detalhes_geracao(id_geracao)

    def consultar_estoque(
        self,
        criterio,
        tipo_deposito,
        limite_posicoes,
        modo_sem_maquina=True,
        criterio_secundario=None
    ):
        self.ultimos_parametros = None
        dados = self.estoque.copy()
        dados = filtrar_tipo_deposito(dados, tipo_deposito)

        if modo_sem_maquina:
            dados = remover_lotes_acima_nivel_1(dados)

        sugestao = criar_sugestao_inventario(dados)

        sugestao = identificar_primeira_contagem(sugestao)

        historico = self._obter_historico()
        sugestao = remover_lotes_historico(sugestao, historico)

        self.sugestao_base = sugestao.copy()

        if criterio == "primeira_contagem" or criterio_secundario == "primeira_contagem":
            sugestao = sugestao[sugestao["nunca_contado"] == True]

        sugestao = priorizar_combinado(sugestao, criterio, criterio_secundario) if criterio_secundario else priorizar_lotes(sugestao, criterio=criterio)

        sugestao = selecionar_lotes(sugestao, limite_posicoes=limite_posicoes)

        return sugestao
