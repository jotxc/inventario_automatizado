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