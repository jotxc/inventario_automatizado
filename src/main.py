from config.entrada_usuario import obter_criterio, obter_limite_posicoes, obter_tipo_deposito
from relatorios.resumo_execucao import mostrar_resumo
from core.inventario import preparar_inventario, executar_inventario


def main():

    try:

        criterio = obter_criterio()
        limite_posicoes = obter_limite_posicoes()
#CARREGAMENTO
        estoque = preparar_inventario()
#INTEGRAÇÃO SUGESTÃO
        tipo_deposito = obter_tipo_deposito(estoque)
        numero_documento = input("\nDigite o número do documento SAP: ")
        resultado = executar_inventario(
                estoque=estoque,
                criterio=criterio,
                limite_posicoes=limite_posicoes,
                tipo_deposito=tipo_deposito,
                numero_documento=numero_documento
        )
        mostrar_resumo(
                sugestao=resultado["sugestao"],
                criterio=resultado["criterio"],
                tipo_deposito=resultado["tipo_deposito"],
                nome_arquivo=resultado["arquivo"]
                )

#TESTE TEMPORÁRIO
        print("\nHistórico atualizado com sucesso!")

    except Exception as erro:

        print("\n" + "=" * 50)
        print("ERRO".center(50))
        print("=" * 50)

        print(f"\n{erro}\n")

        print(
            "Se o problema persistir, verifique:\n"
            "- Arquivos de entrada\n"
            "- Colunas obrigatórias\n"
            "- Tipo de depósito selecionado\n"
            "- Limite de posições\n"
        )

        print("=" * 50)

            
if __name__ == "__main__":
    main()