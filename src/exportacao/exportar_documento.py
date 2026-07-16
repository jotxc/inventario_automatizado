import pandas as pd
from pathlib import Path
from openpyxl import load_workbook
from openpyxl.styles import Font
from openpyxl.styles import Alignment


def exportar_documento(
    estoque,
    nome_arquivo
):

    caminho = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "saida"
    )

    caminho.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo = caminho / nome_arquivo

    estoque.to_excel(
        arquivo,
        index=False
    )

    workbook = load_workbook(arquivo)

    worksheet = workbook.active

    # Cabeçalho

    for celula in worksheet[1]:

        celula.font = Font(bold=True)

        celula.alignment = Alignment(
            horizontal="center"
        )

    # Filtros

    worksheet.auto_filter.ref = worksheet.dimensions

    # Congelar primeira linha

    worksheet.freeze_panes = "A2"

    # Ajustar largura das colunas

    for coluna in worksheet.columns:

        tamanho = max(

            len(str(c.value))

            if c.value is not None

            else 0

            for c in coluna

        )

        worksheet.column_dimensions[
            coluna[0].column_letter
        ].width = tamanho + 2

    print(f"\nArquivo será salvo em:\n{arquivo}\n")

    workbook.save(arquivo)