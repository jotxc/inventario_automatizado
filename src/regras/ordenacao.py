import pandas as pd

def ordenar_posicoes(estoque, baixas_por_ultimo=False):

    if baixas_por_ultimo:
        estoque = estoque.copy()
        estoque["_eh_baixo"] = estoque["nivel"] == 1
        estoque = estoque.sort_values(
            by=["_eh_baixo", "rua", "numero_posicao", "prioridade_posicao", "nivel", "sufixo"],
            ascending=[True, True, True, True, False, True]
        )
        estoque = estoque.drop(columns=["_eh_baixo"])
    else:
        estoque = estoque.sort_values(
            by=[
                "rua",
                "numero_posicao",
                "prioridade_posicao",
                "nivel",
                "sufixo"
            ]
        )

    return estoque.reset_index(drop=True)