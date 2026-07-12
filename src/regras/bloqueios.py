import pandas as pd

#Bloquear Lotes que possuem pelo menos um registro dentro de ordem

def identificar_lotes_em_ordem(estoque):

    lotes_em_ordem = (
        estoque.groupby(
            ["lote", "tipo_deposito"])["estoque_saida"]
        .max()
        .reset_index()
    )

    lotes_em_ordem["possui_ordem"] = (
        lotes_em_ordem["estoque_saida"] > 0
    )

    lotes_em_ordem = lotes_em_ordem[
        ["lote", "tipo_deposito", "possui_ordem"]
    ]

    return lotes_em_ordem

def remover_lotes_em_ordem(estoque):
     
    lotes_em_ordem = identificar_lotes_em_ordem(estoque)
     
    estoque = estoque.merge(
        lotes_em_ordem,
        on=["lote", "tipo_deposito"],
        how="left"
    )

    print(estoque["possui_ordem"].dtype)
    print(estoque["possui_ordem"].value_counts(dropna=False))

    estoque = estoque[ ~estoque["possui_ordem"] ]

    estoque = estoque.drop(
        columns=["possui_ordem"])
   
    return estoque

#Bloquear posições do 330 que possuem pelo menos um registro dentro de ordem

def identificar_posicoes_330_em_ordem(estoque):

    estoque_330 = estoque[
        estoque["tipo_deposito"] == "330"
    ]

    posicoes_bloqueadas = (
        estoque_330.groupby(
            ["posicao", "tipo_deposito"])["estoque_saida"]
        .max()
        .reset_index()
    )

    posicoes_bloqueadas["bloquear_posicao"] = (
        posicoes_bloqueadas["estoque_saida"] > 0
    )

    posicoes_bloqueadas = posicoes_bloqueadas[
        ["posicao", "tipo_deposito", "bloquear_posicao"]
    ]

    return posicoes_bloqueadas

def remover_posicoes_330_em_ordem(estoque):

    posicoes_bloqueadas = identificar_posicoes_330_em_ordem(estoque)

    estoque = estoque.merge(
        posicoes_bloqueadas,
        on=["posicao", "tipo_deposito"],
        how="left"
    )

    estoque["bloquear_posicao"] = (
        estoque["bloquear_posicao"].fillna(False).astype(bool)
    )

    estoque = estoque[
        ~estoque["bloquear_posicao"]
    ]

    estoque = estoque.drop(
        columns=["bloquear_posicao"]
    )

    return estoque

#Excluir lotes que possuam pelo menos um registro acima do nível 100.

def remover_lotes_acima_nivel_1(estoque):

    lotes_nivel = (
    estoque.groupby(
        ["lote", "tipo_deposito"])["nivel"]
        .max()
        .reset_index()
    )

    lotes_nivel["bloquear_lote"] = (
        lotes_nivel["nivel"] > 1
    )

    estoque = estoque.merge(
        lotes_nivel,
        on=["lote", "tipo_deposito"],
        how="left"
    )

    estoque = estoque[
        ~estoque["bloquear_lote"]
    ]

    estoque = estoque.drop(
        columns=["bloquear_lote"]
    )

    return estoque
