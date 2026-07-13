import pandas as pd


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