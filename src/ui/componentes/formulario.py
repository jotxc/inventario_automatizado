from ui.tema import COR_PRIMARIA, COR_SUCESSO, COR_SUCESSO_HOVER, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO
import customtkinter as ctk


class Formulario(ctk.CTkFrame):

    def __init__(self, master, ao_gerar=None, **kwargs):
        super().__init__(master, **kwargs)
        self.ao_gerar = ao_gerar

        self.grid_columnconfigure(0, weight=1)

        self.criar_campo_criterio()
        self.criar_campo_tipo()
        self.criar_campo_limite()
        self.criar_switch_modo()
        self.criar_botao()

    def _criar_label(self, texto):
        label = ctk.CTkLabel(
            self,
            text=texto,
            font=("Segoe UI", 13, "bold"),
            text_color=COR_PRIMARIA,
            anchor="w"
        )
        return label

    def criar_campo_criterio(self):
        label = self._criar_label("Crit\u00e9rio")
        label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        self.combo_criterio = ctk.CTkComboBox(
            self,
            values=[
                "Primeira Contagem",
                "Dias sem Contagem",
                "Valor do Lote"
            ],
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_TEXTO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            dropdown_fg_color=COR_TEXTO_BRANCO,
            dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_PRIMARIA
        )
        self.combo_criterio.grid(row=1, column=0, sticky="ew", padx=20)

    def criar_campo_tipo(self):
        label = self._criar_label("Tipo de dep\u00f3sito")
        label.grid(row=2, column=0, sticky="w", padx=20, pady=(20, 5))

        self.combo_tipo = ctk.CTkComboBox(
            self,
            values=[],
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_TEXTO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            dropdown_fg_color=COR_TEXTO_BRANCO,
            dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_PRIMARIA
        )
        self.combo_tipo.grid(row=3, column=0, sticky="ew", padx=20)

    def criar_campo_limite(self):
        label = self._criar_label("Limite de posi\u00e7\u00f5es")
        label.grid(row=4, column=0, sticky="w", padx=20, pady=(20, 5))

        self.entry_limite = ctk.CTkEntry(
            self,
            placeholder_text="Ex: 100",
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO
        )
        self.entry_limite.insert(0, "100")
        self.entry_limite.grid(row=5, column=0, sticky="ew", padx=20)

    def criar_switch_modo(self):
        frame_switch = ctk.CTkFrame(self, fg_color="transparent")
        frame_switch.grid(row=6, column=0, pady=(15, 0), padx=20, sticky="ew")
        frame_switch.grid_columnconfigure(0, weight=1)

        self.switch_modo = ctk.CTkSwitch(
            frame_switch,
            text="Modo sem m\u00e1quina",
            font=("Segoe UI", 13),
            progress_color=COR_PRIMARIA,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            onvalue=True,
            offvalue=False
        )
        self.switch_modo.select()
        self.switch_modo.grid(row=0, column=0, sticky="w")

    def criar_botao(self):
        self.botao_gerar = ctk.CTkButton(
            self,
            text="\u25B6  GERAR DOCUMENTO",
            font=("Segoe UI", 14, "bold"),
            command=self._ao_gerar,
            fg_color=COR_SUCESSO,
            hover_color=COR_SUCESSO_HOVER,
            text_color=COR_TEXTO_BRANCO,
            height=45,
            corner_radius=8
        )
        self.botao_gerar.grid(row=7, column=0, pady=30, padx=20, sticky="ew")

    def _ao_gerar(self):
        if self.ao_gerar:
            self.ao_gerar()
