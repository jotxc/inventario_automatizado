from importacao.importar_lx02 import carregar_lx02
from importacao.importar_ymm141 import carregar_ymm141
from servicos.preparar_estoque import renomear_colunas, validar_colunas, remover_linhas_vazias  
from servicos.preparar_ymm141 import renomear_colunas_ymm141,validar_colunas_ymm141
from integracoes.ymm141 import resumir_ultima_contagem
from util.posicoes import extrair_rua, extrair_nivel, extrair_numero
from regras.filtros import remover_posicoes_controladas
from regras.bloqueios import remover_lotes_em_ordem, remover_posicoes_330_em_ordem, remover_lotes_acima_nivel_1

def main():

#CARREGAMENTO
    estoque = carregar_lx02()
    print(f"Inicial: {len(estoque)}")
    ymm141 = carregar_ymm141()
#PREPARAÇÃO LX02
    estoque = renomear_colunas(estoque)
    estoque = validar_colunas(estoque)
    estoque = remover_linhas_vazias(estoque)
#PREPARAÇÃO YMM141
    ymm141 = renomear_colunas_ymm141(ymm141)
    ymm141 = validar_colunas_ymm141(ymm141)
#REGRAS LX02
    estoque = remover_posicoes_controladas(estoque)
    print(f"Após remover posições controladas: {len(estoque)}")
    estoque["rua"] = estoque["posicao"].apply(extrair_rua)
    estoque["nivel"] = estoque["posicao"].apply(extrair_nivel)
    estoque["numero_posicao"] = estoque["posicao"].apply(extrair_numero)
    estoque = remover_lotes_em_ordem(estoque)
    print(f"Após remover lotes em ordem: {len(estoque)}")
    estoque = remover_posicoes_330_em_ordem(estoque)
    print(f"Após remover posições 330 em ordem: {len(estoque)}")
    estoque = remover_lotes_acima_nivel_1(estoque)
    print(f"Após modo sem máquina: {len(estoque)}")
#INTEGRAÇÃO YMM141
    resumo_ymm141 = resumir_ultima_contagem(ymm141)

    print()
    print("Resumo YMM141")
    print(len(resumo_ymm141))
    print(resumo_ymm141.head(20))
    
if __name__ == "__main__":
    main()