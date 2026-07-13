from pathlib import Path
import pandas as pd


def carregar_ymm141():

    caminho_projeto = Path(__file__).resolve().parents[2]

    caminho_arquivo = (
        caminho_projeto
        / "data"
        / "entrada"
        / "YMM141.xlsx"
    )

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            "Arquivo YMM141.xlsx não encontrado."
        )

    ymm141 = pd.read_excel(caminho_arquivo)

    return ymm141