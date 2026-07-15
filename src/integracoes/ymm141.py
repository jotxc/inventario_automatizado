import pandas as pd
from datetime import datetime

def resumir_ultima_contagem(ymm141):

    resumo = (
        ymm141
        .sort_values("data_contagem")
        .groupby(
            ["lote", "tipo_deposito"],
            as_index=False
        )
        .last()
    )

    return resumo

def integrar_ultima_contagem(
    estoque,
    resumo_ymm141
):

    colunas = [
        "lote",
        "tipo_deposito",
        "documento_inventario",
        "data_contagem",
        "quantidade_sistema",
        "quantidade_contada"
    ]

    estoque = estoque.merge(
        resumo_ymm141[colunas],
        on=[
            "lote",
            "tipo_deposito"
        ],
        how="left"
    )

    return estoque

def calcular_dias_sem_contagem(estoque):

    hoje = datetime.today()

    estoque["data_contagem"] = (
        pd.to_datetime(
            estoque["data_contagem"],
            errors="coerce"
        )
    )

    estoque["dias_sem_contagem"] = (
        hoje - estoque["data_contagem"]
    ).dt.days

    return estoque