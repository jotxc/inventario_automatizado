from datetime import datetime
from pathlib import Path
import pandas as pd


def criar_historico_documento(
    estoque,
    documento
):

    historico = (
        estoque[
            [
                "material",
                "lote",
                "tipo_deposito"
            ]
        ]
        .drop_duplicates()
        .copy()
    )

    historico["documento"] = documento

    historico["data_geracao"] = (
        datetime.now()
    )

    return historico


def salvar_historico_documento(historico):

    caminho = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "historico"
    )

    caminho.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo = caminho / "historico_documentos.xlsx"

    if arquivo.exists():

        historico_antigo = pd.read_excel(arquivo)

        historico = pd.concat(
            [
                historico_antigo,
                historico
            ],
            ignore_index=True
        )

    print(f"\nHistórico será salvo em:\n{arquivo}\n")

    historico.to_excel(
        arquivo,
        index=False
    )

def carregar_historico_documentos():

    caminho = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "historico"
        / "historico_documentos.xlsx"
    )

    if not caminho.exists():
        return pd.DataFrame()

    return pd.read_excel(caminho)


def remover_lotes_historico(
    sugestao,
    historico
):

    if historico.empty:
        return sugestao

    lotes_bloqueados = (
        historico["lote"]
        .astype(str)
        .unique()
    )

    sugestao = sugestao[
        ~sugestao["lote"].isin(
            lotes_bloqueados
        )
    ]

    return sugestao