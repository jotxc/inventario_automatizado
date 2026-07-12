import pandas as pd


def extrair_rua(posicao):

    if pd.isna(posicao):
        return None
    
    return posicao[:3]


def eh_posicao_especial(posicao):

    if pd.isna(posicao):
        return False
    
    return "W" in posicao


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