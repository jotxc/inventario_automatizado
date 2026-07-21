from importacao.importar_lx02 import carregar_lx02
from importacao.importar_ymm141 import carregar_ymm141
from importacao.importar_custos import carregar_custos

from servicos.preparar_estoque import (
    renomear_colunas,
    validar_colunas,
    remover_linhas_vazias
)

from servicos.preparar_ymm141 import (
    renomear_colunas_ymm141,
    validar_colunas_ymm141,
    remover_linhas_vazias_ymm141
)

from servicos.preparar_custos import (
    renomear_colunas_custos,
    validar_colunas_custos
)

from util.posicoes import preparar_posicoes

from regras.filtros import (
    remover_posicoes_controladas,
    filtrar_tipo_deposito
)

from regras.bloqueios import (
    remover_lotes_em_ordem,
    remover_posicoes_330_em_ordem,
    remover_lotes_acima_nivel_1
)

from integracoes.ymm141 import (
    resumir_ultima_contagem,
    integrar_ultima_contagem,
    calcular_dias_sem_contagem
)

from integracoes.custos import (
    integrar_custos,
    calcular_valor_lote
)

from integracoes.sugestao import (
    criar_sugestao_inventario,
    identificar_primeira_contagem
)

from regras.priorizacao import priorizar_lotes
from regras.selecao import selecionar_lotes, selecionar_posicoes
from regras.ordenacao import ordenar_posicoes

from exportacao.exportar_documento import exportar_documento

from historico.historico_documentos import (
    criar_historico_documento,
    salvar_historico_documento,
    carregar_historico_documentos,
    remover_lotes_historico
)


def preparar_inventario():

    estoque = carregar_lx02()
    ymm141 = carregar_ymm141()
    custos = carregar_custos()

    estoque = renomear_colunas(estoque)
    estoque = validar_colunas(estoque)
    estoque = remover_linhas_vazias(estoque)

    ymm141 = renomear_colunas_ymm141(ymm141)
    ymm141 = validar_colunas_ymm141(ymm141)
    ymm141 = remover_linhas_vazias_ymm141(ymm141)

    custos = renomear_colunas_custos(custos)
    custos = validar_colunas_custos(custos)

    estoque = remover_posicoes_controladas(estoque)
    estoque = preparar_posicoes(estoque)
    estoque = remover_lotes_em_ordem(estoque)
    estoque = remover_posicoes_330_em_ordem(estoque)

    resumo = resumir_ultima_contagem(ymm141)

    estoque = integrar_ultima_contagem(
        estoque,
        resumo
    )

    estoque = calcular_dias_sem_contagem(estoque)

    estoque = integrar_custos(
        estoque,
        custos
    )

    estoque = calcular_valor_lote(estoque)

    return estoque


def executar_inventario(
    estoque,
    criterio,
    limite_posicoes,
    tipo_deposito,
    numero_documento="",
    modo_sem_maquina=True
):

    print("\nANTES DO FILTRO:", len(estoque))

    estoque = filtrar_tipo_deposito(
        estoque,
        tipo_deposito
    )

    print("DEPOIS DO FILTRO:", len(estoque))

    if modo_sem_maquina:
        estoque = remover_lotes_acima_nivel_1(estoque)
        print("DEPOIS DO MODO SEM MAQUINA:", len(estoque))

    sugestao = criar_sugestao_inventario(estoque)

    print("APÓS CRIAR SUGESTÃO:", len(sugestao))

    sugestao = identificar_primeira_contagem(
        sugestao
    )

    print("APÓS PRIMEIRA CONTAGEM:", len(sugestao))

    historico = carregar_historico_documentos()
    sugestao = remover_lotes_historico(sugestao, historico)
    print("APÓS REMOVER HISTÓRICO:", len(sugestao))

    sugestao = priorizar_lotes(
        sugestao,
        criterio=criterio
    )

    print("APÓS PRIORIZAÇÃO:", len(sugestao))

    sugestao = selecionar_lotes(
        sugestao,
        limite_posicoes=limite_posicoes
    )

    print("APÓS SELEÇÃO:", len(sugestao))

    estoque_selecionado = selecionar_posicoes(
        estoque,
        sugestao
    )

    print("ESTOQUE SELECIONADO:", len(estoque_selecionado))

    estoque_selecionado = ordenar_posicoes(
        estoque_selecionado
    )

    exportar_documento(
        estoque_selecionado,
        "Documento_Inventario.xlsx"
    )

    historico = criar_historico_documento(
        estoque_selecionado,
        numero_documento
    )

    salvar_historico_documento(
        historico
    )

    return {
        "criterio": criterio,
        "tipo_deposito": tipo_deposito,
        "arquivo": "Documento_Inventario.xlsx",
        "sugestao": sugestao,
        "estoque": estoque_selecionado
    }