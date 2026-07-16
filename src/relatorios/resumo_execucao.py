import pandas as pd

def mostrar_resumo(
    sugestao,
    criterio,
    tipo_deposito,
    nome_arquivo
):

    total_lotes = len(sugestao)

    total_posicoes = int(
        sugestao["quantidade_posicoes"].sum()
    )

    valor_total = (
        sugestao["valor_lote"].sum()
    )

    primeiras_contagens = int(
        sugestao["nunca_contado"].sum()
    )

    recontagens = (
        total_lotes
        - primeiras_contagens
    )

    print("\n" + "=" * 50)
    print("RESUMO DA EXECUÇÃO".center(50))
    print("=" * 50)

    print(f"Critério.............: {criterio}")

    print(f"Tipo depósito........: {tipo_deposito}")

    print(f"Lotes................: {total_lotes}")

    print(f"Posições.............: {total_posicoes}")

    print(f"Valor total..........: R$ {valor_total:,.2f}")

    print(f"Primeiras contagens..: {primeiras_contagens}")

    print(f"Recontagens..........: {recontagens}")

    print(f"Arquivo..............: {nome_arquivo}")

    print("=" * 50)