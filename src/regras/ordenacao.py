import pandas as pd

def ordenar_posicoes(estoque):

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