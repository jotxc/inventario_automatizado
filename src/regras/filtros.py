def remover_posicoes_controladas(estoque):

    estoque = estoque[
        ~estoque["posicao"].str.startswith("CON")
    ]

    return estoque