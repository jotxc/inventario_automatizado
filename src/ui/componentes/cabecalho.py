from ui.tema import COR_PRIMARIA_ESCURA, COR_TEXTO_BRANCO
import customtkinter as ctk


class Cabecalho(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COR_PRIMARIA_ESCURA,
            corner_radius=0,
            **kwargs
        )

        titulo = ctk.CTkLabel(
            self,
            text="\U0001F4E6  GERADOR DE INVENTÁRIO",
            font=("Segoe UI", 28, "bold"),
            text_color=COR_TEXTO_BRANCO
        )
        titulo.pack(pady=(28, 2))

        subtitulo = ctk.CTkLabel(
            self,
            text="Automatização de Inventário Rotativo",
            font=("Segoe UI", 14),
            text_color=COR_TEXTO_BRANCO
        )
        subtitulo.pack(pady=(0, 28))
