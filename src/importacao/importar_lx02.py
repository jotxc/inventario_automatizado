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

    estoque = pd.read_excel(caminho_arquivo, engine="calamine")

    coluna = "Data da entrada de mercadorias"
    valores_crus = estoque[coluna].copy()

    estoque[coluna] = pd.to_datetime(
        estoque[coluna],
        dayfirst=True,
        errors="coerce"
    )

    na_mask = estoque[coluna].isna()
    if na_mask.any():
        print(f"[DEBUG] {na_mask.sum()} datas não parseadas.")
        print(f"[DEBUG] Amostra (valores crus): {valores_crus[na_mask].head(10).tolist()}")
        print(f"[DEBUG] Tipos: {[type(v).__name__ for v in valores_crus[na_mask].head(10)]}")

    return estoque