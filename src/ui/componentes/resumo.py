from ui.tema import COR_CARD, COR_BORDA, COR_TEXTO, COR_PRIMARIA
import customtkinter as ctk


class CartaoMetrica(ctk.CTkFrame):

    def __init__(self, master, icone, rotulo, **kwargs):
        super().__init__(
            master,
            fg_color=COR_CARD,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=8,
            **kwargs
        )

        self.grid_columnconfigure(0, weight=1)

        self.label_icone_valor = ctk.CTkLabel(
            self,
            text=icone,
            font=("Segoe UI", 22),
            text_color=COR_TEXTO
        )
        self.label_icone_valor.grid(row=0, column=0, pady=(15, 2))

        self.label_rotulo = ctk.CTkLabel(
            self,
            text=rotulo,
            font=("Segoe UI", 11),
            text_color=COR_TEXTO
        )
        self.label_rotulo.grid(row=1, column=0, pady=(0, 15))

    def atualizar_valor(self, texto):
        self.label_icone_valor.configure(text=texto)


class Resumo(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Resumo da Execução",
            font=("Segoe UI", 18, "bold"),
            text_color=COR_PRIMARIA
        )
        titulo.grid(row=0, column=0, pady=(15, 15))

        self.cartao_lotes = CartaoMetrica(self, "\U0001F4E6  0", "Lotes")
        self.cartao_lotes.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.cartao_posicoes = CartaoMetrica(self, "\U0001F4CD  0", "Posições")
        self.cartao_posicoes.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.cartao_valor = CartaoMetrica(self, "\U0001F4B0  R$ 0,00", "Valor Total")
        self.cartao_valor.grid(row=3, column=0, padx=20, pady=(0, 10), sticky="ew")

        self.label_arquivo = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO,
            anchor="w",
            wraplength=250
        )
        self.label_arquivo.grid(row=4, column=0, padx=20, pady=(0, 5), sticky="w")

        self.label_estado = ctk.CTkLabel(
            self,
            text="Nenhum documento gerado.",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO,
            anchor="w"
        )
        self.label_estado.grid(row=5, column=0, padx=20, pady=(0, 20), sticky="w")

    def limpar(self):
        self.cartao_lotes.atualizar_valor("\U0001F4E6  0")
        self.cartao_posicoes.atualizar_valor("\U0001F4CD  0")
        self.cartao_valor.atualizar_valor("\U0001F4B0  R$ 0,00")
        self.label_arquivo.configure(text="")
        self.label_estado.configure(text="Nenhum documento gerado.")

    def atualizar(self, dados):
        self.cartao_lotes.atualizar_valor(f"\U0001F4E6  {dados['lotes']}")
        self.cartao_posicoes.atualizar_valor(f"\U0001F4CD  {dados['posicoes']}")
        valor_formatado = f"R$ {dados['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self.cartao_valor.atualizar_valor(f"\U0001F4B0  {valor_formatado}")
        self.label_arquivo.configure(text=f"\U0001F4C4  {dados['arquivo']}")
        self.label_estado.configure(text="Documento gerado com sucesso.")
