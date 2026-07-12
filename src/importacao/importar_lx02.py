from pathlib import Path

import pandas as pd


def carregar_lx02():
    """
    Lê o arquivo LX02 localizado na pasta data/entrada
    e retorna um DataFrame.
    """

    caminho_projeto = Path(__file__).resolve().parents[2]

    caminho_arquivo = caminho_projeto / "data" / "entrada" / "LX02.xlsx"

    if not caminho_arquivo.exists():
        raise FileNotFoundError(
            "Arquivo LX02.xlsx não encontrado.\n"
            "Coloque o arquivo na pasta data/entrada."
        )

    estoque = pd.read_excel(caminho_arquivo)

    return estoque