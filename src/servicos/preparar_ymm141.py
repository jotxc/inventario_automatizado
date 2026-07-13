from core.colunas import COLUNAS_YMM141

COLUNAS_OBRIGATORIAS_YMM141 = [
    "documento_inventario",
    "material",
    "lote",
    "tipo_deposito",
    "data_contagem",
    "quantidade_sistema",
]   

def renomear_colunas_ymm141(ymm141):

    return ymm141.rename(
        columns=COLUNAS_YMM141
    )

def validar_colunas_ymm141(ymm141):

    faltando = [
        coluna
        for coluna in COLUNAS_OBRIGATORIAS_YMM141
        if coluna not in ymm141.columns
    ]

    if faltando:
        raise ValueError(
            f"Colunas ausentes: {faltando}"
        )

    return ymm141