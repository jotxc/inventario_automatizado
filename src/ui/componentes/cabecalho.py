from ui.tema import COR_PRIMARIA_ESCURA, COR_TEXTO_BRANCO
import customtkinter as ctk


class Cabecalho(ctk.CTkFrame):

    def __init__(self, master, titulo="GERADOR DE INVENT\u00c1RIO", subtitulo="Automatiza\u00e7\u00e3o de Invent\u00e1rio Rotativo", **kwargs):
        super().__init__(
            master,
            fg_color=COR_PRIMARIA_ESCURA,
            corner_radius=0,
            **kwargs
        )

        self.label_titulo = ctk.CTkLabel(
            self,
            text=f"\U0001F4E6  {titulo}",
            font=("Segoe UI", 28, "bold"),
            text_color=COR_TEXTO_BRANCO
        )
        self.label_titulo.pack(pady=(28, 2))

        self.label_subtitulo = ctk.CTkLabel(
            self,
            text=subtitulo,
            font=("Segoe UI", 14),
            text_color=COR_TEXTO_BRANCO
        )
        self.label_subtitulo.pack(pady=(0, 28))
