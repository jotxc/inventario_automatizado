import pandas as pd

def integrar_custos(
    estoque,
    custos
):

    custos = custos[
        [
            "material",
            "custo_unitario"
        ]
    ]

    estoque = estoque.merge(
        custos,
        on="material",
        how="left"
    )

    return estoque

def calcular_valor_lote(estoque):

    estoque["valor_lote"] = (

        estoque["estoque_total"]

        *

        estoque["custo_unitario"]

    )

    return estoque