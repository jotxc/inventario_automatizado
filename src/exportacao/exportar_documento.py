import pandas as pd


def exportar_documento(estoque, caminho):

    colunas_sap = [
        "posicao"
    ]

    colunas_conferencia = [
        "posicao",
        "material",
        "descricao_material",
        "lote",
        "tipo_deposito",
        "estoque_total",
        "valor_lote"
    ]


    with pd.ExcelWriter(caminho) as writer:

        estoque[
            colunas_sap
        ].to_excel(
            writer,
            sheet_name="SAP",
            index=False
        )


        estoque[
            colunas_conferencia
        ].to_excel(
            writer,
            sheet_name="Conferencia",
            index=False
        )