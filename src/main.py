from importacao.importar_lx02 import carregar_lx02
from servicos.preparar_estoque import renomear_colunas, validar_colunas, remover_linhas_vazias
from util.posicoes import extrair_rua, extrair_nivel, extrair_numero
from regras.filtros import remover_posicoes_controladas
from regras.bloqueios import remover_lotes_em_ordem, remover_posicoes_330_em_ordem, remover_lotes_acima_nivel_1

def main():

    estoque = carregar_lx02()
    print(f"Inicial: {len(estoque)}")
    estoque = renomear_colunas(estoque)
    estoque = validar_colunas(estoque)
    estoque = remover_linhas_vazias(estoque)
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

    print(
    estoque[
        ["posicao", "rua", "nivel", "numero_posicao"]
    ].head(20)
)


if __name__ == "__main__":
    main()