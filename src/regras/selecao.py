import pandas as pd

def selecionar_lotes(sugestao, limite_posicoes=100):

    sugestao = sugestao.copy()

    total_posicoes = 0

    selecionados = []

    for indice, lote in sugestao.iterrows():

        quantidade = lote["quantidade_posicoes"]

        if total_posicoes + quantidade <= limite_posicoes:

            selecionados.append(indice)

            total_posicoes += quantidade

    return sugestao.loc[selecionados]

def selecionar_posicoes(estoque, sugestao):

    lotes = sugestao[
        [
            "lote",
            "tipo_deposito"
        ]
    ]

    estoque = estoque.merge(

        lotes,

        on=[
            "lote",
            "tipo_deposito"
        ],

        how="inner"

    )

    return estoque