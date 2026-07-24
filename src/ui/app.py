import customtkinter as ctk

from ui.telas.visualizacao_estoque import TelaVisualizacaoEstoque
from ui.telas.resultado import TelaResultado
from controller.inventario_controller import InventarioController


class Aplicacao(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Gerador de Invent\u00e1rio")

        self.geometry("1200x900")

        self.minsize(1000, 650)

        ctk.set_appearance_mode("light")

        ctk.set_default_color_theme("blue")

        self.container = ctk.CTkFrame(self, fg_color="transparent")
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.controller = InventarioController()

        self.tela_principal = None
        self.tela_resultado = None

        self._criar_tela_principal()
        self.mostrar_principal()

    def _criar_tela_principal(self):

        self.tela_principal = TelaVisualizacaoEstoque(
            self.container,
            controller=self.controller,
            ao_exibir_resultado=self.mostrar_resultado
        )
        self.tela_principal.grid(row=0, column=0, sticky="nsew")

    def mostrar_principal(self):

        if self.tela_resultado is not None:
            self.tela_resultado.grid_forget()
            self.tela_resultado = None

        self.tela_principal.grid(row=0, column=0, sticky="nsew")
        self.tela_principal._atualizar_botao_ver_documento()

    def mostrar_resultado(self, resultado):

        self.tela_principal.grid_forget()

        self.tela_resultado = TelaResultado(
            self.container,
            resultado=resultado,
            ao_voltar=self.mostrar_principal
        )
        self.tela_resultado.grid(row=0, column=0, sticky="nsew")


def iniciar():

    app = Aplicacao()

    app.mainloop()