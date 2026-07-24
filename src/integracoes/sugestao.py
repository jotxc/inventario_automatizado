import pandas as pd

def criar_sugestao_inventario(estoque):

    sugestao = (

        estoque.groupby(

            [
                "material",
                "descricao_material",
                "lote",
                "tipo_deposito"
            ],

            as_index=False

        ).agg(

            quantidade_posicoes=(
                "posicao",
                "count"
            ),

            estoque_total=(
                "estoque_total",
                "sum"
            ),

            valor_lote=(
                "valor_lote",
                "sum"
            ),

            ultima_contagem=(
                "data_contagem",
                "max"
            ),

            dias_sem_contagem=(
                "dias_sem_contagem",
                "max"
            )

        )

    )

    return sugestao

def identificar_primeira_contagem(sugestao):

    sugestao["nunca_contado"] = (
        sugestao["ultima_contagem"].isna()
    )

    return sugestao