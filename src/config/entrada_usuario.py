from config.config import (
    CRITERIOS_DISPONIVEIS,
    LIMITE_PADRAO_POSICOES
)


def obter_criterio():

    print("\n===== GERADOR DE INVENTÁRIO =====")

    print("\nCritério de priorização:")

    print("1 - Primeira contagem")
    print("2 - Dias sem contagem")
    print("3 - Valor do lote")
    print("4 - Menos posições")

    escolha = int(input("\nEscolha: "))

    return CRITERIOS_DISPONIVEIS.get(
        escolha,
        "primeira_contagem"
    )


def obter_limite_posicoes():

    limite = input(
        f"\nLimite de posições [{LIMITE_PADRAO_POSICOES}]: "
    )

    if limite == "":
        return LIMITE_PADRAO_POSICOES

    return int(limite)


def obter_tipo_deposito(estoque):

    resumo = (
        estoque
        .groupby("tipo_deposito")
        .agg(
            lotes=("lote", "nunique"),
            posicoes=("posicao", "count"),
            valor=("valor_lote", "sum")
        )
        .reset_index()
        .sort_values("tipo_deposito")
    )

    print("\nTipos de depósito disponíveis:\n")

    for indice, linha in enumerate(
        resumo.itertuples(),
        start=1
    ):

        print(
            f"{indice} - {int(linha.tipo_deposito)} | "
            f"{linha.lotes} lotes | "
            f"{linha.posicoes} posições | "
            f"R$ {linha.valor:,.2f}"
        )

    opcao = int(input("\nEscolha: "))

    return int(
        resumo.iloc[opcao - 1]["tipo_deposito"]
    )