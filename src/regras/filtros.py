import pandas as pd

def remover_posicoes_controladas(estoque):

    estoque = estoque[
        ~estoque["posicao"].str.startswith("CON")
    ]

    return estoque

def normalizar_tipo_deposito(valor):
    try:
        return str(int(float(str(valor))))
    except (ValueError, TypeError):
        return str(valor)

def filtrar_tipo_deposito(estoque, tipo_deposito):

    estoque = estoque.copy()

    estoque["tipo_deposito"] = (
        estoque["tipo_deposito"]
        .apply(normalizar_tipo_deposito)
    )

    tipo_deposito = normalizar_tipo_deposito(tipo_deposito)

    return estoque[
        estoque["tipo_deposito"] == tipo_deposito
    ]