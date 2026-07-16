import pandas as pd

def remover_posicoes_controladas(estoque):

    estoque = estoque[
        ~estoque["posicao"].str.startswith("CON")
    ]

    return estoque

def filtrar_tipo_deposito(estoque, tipo_deposito):

    return estoque[
        estoque["tipo_deposito"] == tipo_deposito
    ].copy()