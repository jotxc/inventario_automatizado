import pandas as pd

def priorizar_por_valor(sugestao):

    return sugestao.sort_values(
        "valor_lote",
        ascending=False
    )


def priorizar_por_antiguidade(sugestao):

    return sugestao.sort_values(
        "dias_sem_contagem",
        ascending=False
    )


def priorizar_por_quantidade_posicoes(sugestao):

    return sugestao.sort_values(
        "quantidade_posicoes",
        ascending=True
    )


def priorizar_por_primeira_contagem(sugestao):

    return sugestao.sort_values(
        [
            "nunca_contado",
            "dias_sem_contagem"
        ],
        ascending=[
            False,
            False
        ]
    )

def priorizar_lotes(sugestao, criterio):

    criterios = {

        "valor": priorizar_por_valor,

        "dias": priorizar_por_antiguidade,

        "posicoes": priorizar_por_quantidade_posicoes,

        "primeira_contagem": priorizar_por_primeira_contagem

    }

    return criterios[criterio](sugestao)


CRITERIO_SORT_MAP = {
    "valor":         (["valor_lote"],             [False]),
    "dias":          (["dias_sem_contagem"],       [False]),
    "posicoes":      (["quantidade_posicoes"],     [True]),
    "primeira_contagem": (["nunca_contado", "dias_sem_contagem"], [False, False]),
}


def priorizar_combinado(sugestao, criterio_primario, criterio_secundario=None):

    cols, asc = CRITERIO_SORT_MAP[criterio_primario]

    if criterio_secundario:
        cols2, asc2 = CRITERIO_SORT_MAP[criterio_secundario]
        for c, a in zip(cols2, asc2):
            if c not in cols:
                cols = cols + [c]
                asc = asc + [a]

    return sugestao.sort_values(cols, ascending=asc)