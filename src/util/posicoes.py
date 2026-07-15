import pandas as pd


def extrair_rua(posicao):

    if pd.isna(posicao):
        return None
    
    return posicao[:3]


def eh_posicao_especial(posicao):

    if pd.isna(posicao):
        return False
    
    return "W" in posicao[3:]


def possui_sufixo(posicao):

    if pd.isna(posicao):
        return False
        
    return posicao[-1].isalpha() and not eh_posicao_especial(posicao)


def extrair_nivel(posicao):
    """
    Retorna o nível físico da posição.

    Exemplos:
    EAE110 -> 1
    EAE212 -> 2
    EAE399 -> 3
    EAB120B -> 1

    Posições especiais retornam None.
    """
    if pd.isna(posicao):
        return None
    
    codigo = posicao[3:]

    if not codigo:
        return None

    if not codigo[0].isdigit():
        return None

    return int(codigo[0])


def extrair_numero(posicao):
    """
    Retorna o número da posição.

    EAE110 -> 10
    EAE125 -> 25
    EAB120B -> 20

    Posições especiais retornam None.
    """

    if pd.isna(posicao):
        return None

    if eh_posicao_especial(posicao):
        return None

    codigo = posicao[3:]

    if possui_sufixo(posicao):
        codigo = codigo[:-1]

    if len(codigo) < 2 or not codigo[1:].isdigit():
        return None

    return int(codigo[1:])

def preparar_posicoes(estoque):

    estoque = estoque.copy()

    estoque["rua"] = (
        estoque["posicao"].apply(extrair_rua)
    )

    estoque["nivel"] = (
        estoque["posicao"].apply(extrair_nivel)
    )

    estoque["numero_posicao"] = (
        estoque["posicao"].apply(extrair_numero)
    )

    estoque["especial"] = (
        estoque["posicao"].apply(eh_posicao_especial)
    )
    
    estoque["prioridade_posicao"] = (
        estoque["especial"]
        .map(
            {
                True: 0,
                False: 1
            }
        )
    )

    estoque["sufixo"] = (
        estoque["posicao"].apply(extrair_sufixo)
    )

    return estoque

def extrair_tipo_posicao(posicao):

    if pd.isna(posicao):
        return None

    if eh_posicao_especial(posicao):
        return 0

    if possui_sufixo(posicao):
        return 2

    return 1

def extrair_sufixo(posicao):

    if pd.isna(posicao):
        return ""

    if possui_sufixo(posicao):
        return posicao[-1]

    return ""