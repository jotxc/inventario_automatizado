import pandas as pd

def remover_posicoes_controladas(estoque):

    estoque = estoque[
        ~estoque["posicao"].str.startswith("CON")
    ]

    return estoque

def filtrar_tipo_deposito(estoque, tipo_deposito):

    estoque = estoque.copy()

    estoque["tipo_deposito"] = (
        estoque["tipo_deposito"]
        .astype(str)
        .str.replace(".0", "", regex=False)
    )

    tipo_deposito = (
        str(tipo_deposito)
        .replace(".0", "")
    )

    return estoque[
        estoque["tipo_deposito"] == tipo_deposito
    ]