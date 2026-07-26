import customtkinter as ctk

from ui.telas.visualizacao_estoque import TelaVisualizacaoEstoque
from ui.telas.visao_geral import TelaVisaoGeral
from ui.telas.resultado import TelaResultado
from ui.telas.historico import TelaHistorico
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
        self.tela_visao_geral = None
        self.tela_historico = None

        self._criar_tela_principal()
        self.mostrar_principal()

    def _criar_tela_principal(self):

        self.tela_principal = TelaVisualizacaoEstoque(
            self.container,
            controller=self.controller,
            ao_exibir_resultado=self.mostrar_resultado,
            ao_exibir_visao_geral=self.mostrar_visao_geral,
            ao_exibir_historico=self.mostrar_historico
        )
        self.tela_principal.grid(row=0, column=0, sticky="nsew")
        self.update_idletasks()

    def mostrar_principal(self):

        if self.tela_resultado is not None:
            self.tela_resultado.grid_forget()
            self.tela_resultado = None

        if self.tela_visao_geral is not None:
            self.tela_visao_geral.grid_forget()
            self.tela_visao_geral = None

        if self.tela_historico is not None:
            self.tela_historico.grid_forget()
            self.tela_historico = None

        self.tela_principal.grid(row=0, column=0, sticky="nsew")

    def mostrar_visao_geral(self):

        self.tela_principal.grid_forget()

        self.tela_visao_geral = TelaVisaoGeral(
            self.container,
            controller=self.controller,
            ao_voltar=self.mostrar_principal
        )
        self.tela_visao_geral.grid(row=0, column=0, sticky="nsew")

    def mostrar_historico(self, ao_voltar=None):

        if ao_voltar is None:
            ao_voltar = self.mostrar_principal

        for screen in [self.tela_principal, self.tela_resultado, self.tela_visao_geral]:
            if screen is not None:
                screen.grid_forget()

        self.tela_historico = TelaHistorico(
            self.container,
            controller=self.controller,
            ao_voltar=ao_voltar,
            ao_visualizar_geracao=lambda r: self.mostrar_resultado(
                r, ao_voltar=lambda: self.mostrar_historico(ao_voltar=ao_voltar)
            )
        )
        self.tela_historico.grid(row=0, column=0, sticky="nsew")

    def mostrar_resultado(self, resultado, ao_voltar=None):

        if ao_voltar is None:
            ao_voltar = self.mostrar_principal

        for screen in [self.tela_principal, self.tela_historico, self.tela_visao_geral]:
            if screen is not None:
                screen.grid_forget()

        self.tela_resultado = TelaResultado(
            self.container,
            resultado=resultado,
            ao_voltar=ao_voltar,
            ao_exibir_historico=lambda: self.mostrar_historico(
                ao_voltar=lambda: self.mostrar_resultado(resultado, ao_voltar=ao_voltar)
            )
        )
        self.tela_resultado.grid(row=0, column=0, sticky="nsew")


def iniciar():

    app = Aplicacao()

    app.mainloop()