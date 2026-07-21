from core.inventario import (
    preparar_inventario,
    executar_inventario
)


class InventarioController:

    def __init__(self):

        self.estoque = None

    def carregar(self):

        self.estoque = preparar_inventario()

        tipos = (
            self.estoque["tipo_deposito"]
            .drop_duplicates()
            .sort_values()
            .astype(str)
            .tolist()
        )

        return tipos

    def gerar(

        self,
        criterio,
        tipo_deposito,
        limite_posicoes,
        modo_sem_maquina=True

    ):

        return executar_inventario(

            estoque=self.estoque,

            criterio=criterio,

            tipo_deposito=tipo_deposito,

            limite_posicoes=limite_posicoes,

            modo_sem_maquina=modo_sem_maquina

        )