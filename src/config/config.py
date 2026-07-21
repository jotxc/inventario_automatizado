import os

CRITERIOS_DISPONIVEIS = {
    1: "primeira_contagem",
    2: "dias",
    3: "valor"
}

LIMITE_PADRAO_POSICOES = 100

MODO_SEM_MAQUINA = True

CRITERIOS_UI = {
    "Primeira Contagem": "primeira_contagem",
    "Dias sem Contagem": "dias",
    "Valor do Lote": "valor"
}

PASTA_RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(PASTA_RAIZ, "data")
ENTRADA_DIR = os.path.join(DATA_DIR, "entrada")
SAIDA_DIR = os.path.join(DATA_DIR, "saida")
HISTORICO_DIR = os.path.join(DATA_DIR, "historico")

ARQUIVO_SAIDA = os.path.join(SAIDA_DIR, "Documento_Inventario.xlsx")
ARQUIVO_HISTORICO = os.path.join(HISTORICO_DIR, "historico_documentos.xlsx")