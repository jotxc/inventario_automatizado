from pathlib import Path
import pandas as pd


def carregar_custos():

    caminho_projeto = Path(__file__).resolve().parents[2]

    caminho_arquivo = (
        caminho_projeto
        / "data"
        / "entrada"
        / "Custos.xlsx"
    )

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            "Arquivo Custos.xlsx não encontrado."
        )

    custos = pd.read_excel(caminho_arquivo)

    return custos