import customtkinter as ctk

from ui.telas.principal import TelaPrincipal


class Aplicacao(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title("Gerador de Inventário")

        self.geometry("1200x900")

        self.minsize(1000, 650)

        ctk.set_appearance_mode("light")

        ctk.set_default_color_theme("blue")

        tela = TelaPrincipal(self)

        tela.pack(
            fill="both",
            expand=True
        )


def iniciar():

    app = Aplicacao()

    app.mainloop()