from core.colunas import COLUNAS_CUSTOS


def renomear_colunas_custos(custos):

    custos = custos.rename(
        columns=COLUNAS_CUSTOS
    )

    return custos


def validar_colunas_custos(custos):

    obrigatorias = [
        "material",
        "custo_unitario"
    ]

    for coluna in obrigatorias:

        if coluna not in custos.columns:

            raise ValueError(
                f"Coluna '{coluna}' não encontrada."
            )

    return custos