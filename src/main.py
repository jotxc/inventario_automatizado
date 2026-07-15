from importacao.importar_lx02 import carregar_lx02
from importacao.importar_ymm141 import carregar_ymm141
from importacao.importar_custos import carregar_custos
from servicos.preparar_estoque import renomear_colunas, validar_colunas, remover_linhas_vazias  
from servicos.preparar_ymm141 import renomear_colunas_ymm141,validar_colunas_ymm141, remover_linhas_vazias_ymm141
from servicos.preparar_custos import renomear_colunas_custos, validar_colunas_custos
from integracoes.ymm141 import resumir_ultima_contagem, integrar_ultima_contagem, calcular_dias_sem_contagem
from integracoes.custos import integrar_custos, calcular_valor_lote
from integracoes.sugestao import criar_sugestao_inventario, identificar_primeira_contagem
from util.posicoes import preparar_posicoes
from regras.filtros import remover_posicoes_controladas
from regras.bloqueios import remover_lotes_em_ordem, remover_posicoes_330_em_ordem, remover_lotes_acima_nivel_1
from regras.priorizacao import priorizar_lotes
from regras.selecao import selecionar_lotes, selecionar_posicoes
from regras.ordenacao import ordenar_posicoes
from exportacao.exportar_documento import exportar_documento

def main():

#CARREGAMENTO
    estoque = carregar_lx02()
    print(f"Inicial: {len(estoque)}")
    ymm141 = carregar_ymm141()
    custos = carregar_custos()
#PREPARAÇÃO LX02
    estoque = renomear_colunas(estoque)
    estoque = validar_colunas(estoque)
    estoque = remover_linhas_vazias(estoque)
#PREPARAÇÃO YMM141
    ymm141 = renomear_colunas_ymm141(ymm141)
    ymm141 = validar_colunas_ymm141(ymm141)
    ymm141 = remover_linhas_vazias_ymm141(ymm141)
#PREPARAÇÃO CUSTOS
    custos = renomear_colunas_custos(custos)
    custos = validar_colunas_custos(custos)
#REGRAS LX02
    estoque = remover_posicoes_controladas(estoque)
    print(f"Após remover posições controladas: {len(estoque)}")
    estoque = preparar_posicoes(estoque)
    estoque = remover_lotes_em_ordem(estoque)
    print(f"Após remover lotes em ordem: {len(estoque)}")
    estoque = remover_posicoes_330_em_ordem(estoque)
    print(f"Após remover posições 330 em ordem: {len(estoque)}")
    estoque = remover_lotes_acima_nivel_1(estoque)
    print(f"Após modo sem máquina: {len(estoque)}")
#INTEGRAÇÃO YMM141
    resumo_ymm141 = resumir_ultima_contagem(ymm141)
    estoque = integrar_ultima_contagem(estoque, resumo_ymm141)
    estoque = calcular_dias_sem_contagem(estoque)
#INTEGRACAO CUSTOS
    estoque = integrar_custos(estoque, custos)
    estoque = calcular_valor_lote(estoque)
#INTEGRAÇÃO SUGESTÃO
    sugestao = criar_sugestao_inventario(estoque)
    sugestao = identificar_primeira_contagem(sugestao)
    sugestao = priorizar_lotes(sugestao, criterio= "primeira_contagem")
    sugestao = selecionar_lotes(sugestao, limite_posicoes= 100)
    estoque_selecionado = selecionar_posicoes(estoque, sugestao)
    estoque_selecionado = ordenar_posicoes(estoque_selecionado)
    exportar_documento(estoque_selecionado, "Documento_Inventario.xlsx")

#TESTE TEMPORÁRIO
    print("\nDocumento final:")

    print(
        estoque_selecionado[
            [
                "posicao",
                "material",
                "descricao_material",
                "lote",
                "rua",
                "nivel",
                "numero_posicao"
            ]
        ].head(30)
    )
            
if __name__ == "__main__":
    main()