from core.colunas import COLUNAS_LX02
from core.colunas import COLUNAS_OBRIGATORIAS


def renomear_colunas(estoque):

    estoque = estoque.rename(
        columns=COLUNAS_LX02
    )

    return estoque

def validar_colunas(estoque):
    
    for coluna in COLUNAS_OBRIGATORIAS:
  
          if coluna not in estoque.columns:
            raise ValueError(
                f"A coluna obrigatória '{coluna}' não foi encontrada."
            )

    return estoque

def remover_linhas_vazias(estoque):

    estoque = estoque.dropna(
        subset=["material"]
    )

    return estoque