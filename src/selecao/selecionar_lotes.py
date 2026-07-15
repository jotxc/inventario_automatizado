import pandas as pd

def filtrar_lotes_escolhidos(estoque, lotes_escolhidos):

    estoque_selecionado = estoque[
        estoque["lote"].isin(lotes_escolhidos)
    ]

    return estoque_selecionado