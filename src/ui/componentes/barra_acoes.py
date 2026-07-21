from ui.tema import COR_PRIMARIA, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO
import customtkinter as ctk


class BarraAcoes(ctk.CTkFrame):

    def __init__(self, master, ao_importar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.ao_importar = ao_importar

        self.grid_columnconfigure(3, weight=1)

        self.botao_documento = ctk.CTkButton(
            self,
            text="\U0001F4C4  Abrir Documento",
            font=("Segoe UI", 13),
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA,
            border_color=COR_PRIMARIA,
            border_width=2,
            state="disabled",
            width=190,
            height=38,
            corner_radius=8
        )
        self.botao_documento.grid(row=0, column=0, padx=(20, 5), pady=15)

        self.botao_historico = ctk.CTkButton(
            self,
            text="\U0001F4CB  Abrir Hist\u00f3rico",
            font=("Segoe UI", 13),
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA,
            border_color=COR_PRIMARIA,
            border_width=2,
            width=190,
            height=38,
            corner_radius=8
        )
        self.botao_historico.grid(row=0, column=1, padx=5, pady=15)

        self.botao_importar = ctk.CTkButton(
            self,
            text="\U0001F4E5  Atualizar Dados",
            font=("Segoe UI", 13),
            fg_color=COR_PRIMARIA,
            text_color=COR_TEXTO_BRANCO,
            hover_color=COR_TEXTO_SECUNDARIO,
            border_color=COR_PRIMARIA,
            border_width=2,
            width=190,
            height=38,
            corner_radius=8,
            command=self._ao_importar
        )
        self.botao_importar.grid(row=0, column=2, padx=5, pady=15)

    def _ao_importar(self):
        if self.ao_importar:
            self.ao_importar()
