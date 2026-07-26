from datetime import datetime
from pathlib import Path
import uuid
import pandas as pd


def criar_historico_documento(
    estoque,
    documento,
    criterio="",
    sugestao=None
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

    id_geracao = str(uuid.uuid4())
    agora = datetime.now()

    historico["documento"] = documento
    historico["data_geracao"] = agora
    historico["id_geracao"] = id_geracao
    historico["criterio"] = criterio

    if sugestao is not None and not sugestao.empty:
        total_lotes = len(sugestao)
        total_posicoes = int(sugestao["quantidade_posicoes"].sum())
        total_valor = sugestao["valor_lote"].sum()

        info = sugestao[["lote", "tipo_deposito", "quantidade_posicoes", "valor_lote"]].copy()
        info["lote"] = info["lote"].astype(str)
        info["tipo_deposito"] = info["tipo_deposito"].astype(str)

        historico["lote"] = historico["lote"].astype(str)
        historico["tipo_deposito"] = historico["tipo_deposito"].astype(str)

        historico = historico.merge(
            info[["lote", "tipo_deposito", "quantidade_posicoes", "valor_lote"]],
            on=["lote", "tipo_deposito"],
            how="left"
        )

        historico["total_lotes_geracao"] = total_lotes
        historico["total_posicoes_geracao"] = total_posicoes
        historico["total_valor_geracao"] = total_valor
    else:
        historico["quantidade_posicoes"] = 0
        historico["valor_lote"] = 0.0
        historico["total_lotes_geracao"] = len(historico)
        historico["total_posicoes_geracao"] = 0
        historico["total_valor_geracao"] = 0.0

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


def carregar_ultima_geracao():

    historico = carregar_historico_documentos()

    if historico.empty:
        return None

    if "id_geracao" not in historico.columns:
        datas = historico["data_geracao"].dropna().unique()
        if len(datas) == 0:
            return None
        ultima_data = max(datas)
        linhas = historico[historico["data_geracao"] == ultima_data]
        if linhas.empty:
            return None
        primeira = linhas.iloc[0]
        return {
            "criterio": "",
            "tipo_deposito": primeira.get("tipo_deposito", ""),
            "data_geracao": primeira.get("data_geracao", ""),
            "id_geracao": "",
            "documento": primeira.get("documento", ""),
            "arquivo": "Documento_Inventario.xlsx",
            "sugestao": linhas,
            "estoque": None,
            "do_historico": True
        }

    ultimo_id = historico["id_geracao"].iloc[-1]

    linhas = historico[historico["id_geracao"] == ultimo_id]

    if linhas.empty:
        return None

    primeira = linhas.iloc[0]

    return {
        "criterio": primeira.get("criterio", ""),
        "tipo_deposito": primeira.get("tipo_deposito", ""),
        "data_geracao": primeira.get("data_geracao", ""),
        "id_geracao": primeira.get("id_geracao", ""),
        "documento": primeira.get("documento", ""),
        "arquivo": "Documento_Inventario.xlsx",
        "sugestao": linhas,
        "estoque": None,
        "do_historico": True
    }


def atualizar_documento_geracao(id_geracao, numero_documento):

    caminho = (
        Path(__file__)
        .resolve()
        .parents[2]
        / "data"
        / "historico"
        / "historico_documentos.xlsx"
    )

    if not caminho.exists():
        return False

    try:
        historico = pd.read_excel(caminho)

        if "id_geracao" not in historico.columns:
            return False

        historico["id_geracao"] = historico["id_geracao"].fillna("").astype(str)
        historico["documento"] = historico["documento"].fillna("").astype(str)
        id_geracao = str(id_geracao)

        mask = historico["id_geracao"] == id_geracao

        if not mask.any():
            return False

        historico.loc[mask, "documento"] = str(numero_documento)
        historico.to_excel(caminho, index=False)
        return True
    except Exception as e:
        print(f"Erro ao atualizar documento: {e}")
        return False


def remover_lotes_historico(
    sugestao,
    historico
):

    if historico.empty:
        return sugestao

    historico = (
        historico[["lote", "tipo_deposito"]]
        .drop_duplicates()
        .copy()
    )

    historico["lote"] = historico["lote"].astype(str)
    historico["tipo_deposito"] = historico["tipo_deposito"].astype(str)

    historico["ja_contado"] = True

    sugestao = sugestao.copy()
    sugestao["lote"] = sugestao["lote"].astype(str)
    sugestao["tipo_deposito"] = sugestao["tipo_deposito"].astype(str)

    sugestao = sugestao.merge(
        historico,
        on=["lote", "tipo_deposito"],
        how="left"
    )

    sugestao = sugestao[
        sugestao["ja_contado"].isna()
    ]

    sugestao = sugestao.drop(
        columns=["ja_contado"]
    )

    return sugestao
