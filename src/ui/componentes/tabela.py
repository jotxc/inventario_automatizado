import tkinter as tk
from tkinter import ttk
import pandas as pd
import customtkinter as ctk

from ui.tema import COR_PRIMARIA, COR_TEXTO, COR_TEXTO_SECUNDARIO, COR_FUNDO, COR_CARD, COR_BORDA


COR_LINHA_1 = "#FFFFFF"
COR_LINHA_2 = "#F0F4F8"
COR_CABECALHO_FUNDO = COR_PRIMARIA
COR_CABECALHO_TEXTO = "#FFFFFF"


class TabelaDados(ctk.CTkFrame):

    def __init__(self, master, colunas, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)

        self.colunas = colunas
        self.colunas_chave = [c["chave"] for c in colunas]
        self.colunas_rotulo = [c["rotulo"] for c in colunas]
        self.colunas_formato = {c["chave"]: c.get("formato") for c in colunas}
        self.colunas_largura = {c["chave"]: c.get("largura", 120) for c in colunas}
        self.colunas_alinhamento = {c["chave"]: c.get("alinhamento", "w") for c in colunas}

        self.dados_originais = None
        self.coluna_ordenada = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        frame_externo = ctk.CTkFrame(self, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        frame_externo.grid(row=0, column=0, sticky="nsew")
        frame_externo.grid_rowconfigure(0, weight=1)
        frame_externo.grid_columnconfigure(0, weight=1)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Tabela.Treeview",
            background=COR_LINHA_1,
            foreground=COR_TEXTO,
            fieldbackground=COR_LINHA_1,
            font=("Segoe UI", 11),
            rowheight=30,
            borderwidth=0
        )
        style.map(
            "Tabela.Treeview",
            background=[("selected", COR_PRIMARIA)],
            foreground=[("selected", COR_CABECALHO_TEXTO)]
        )

        style.configure(
            "Tabela.Treeview.Heading",
            background=COR_CABECALHO_FUNDO,
            foreground=COR_CABECALHO_TEXTO,
            font=("Segoe UI", 11, "bold"),
            borderwidth=0,
            relief="flat"
        )
        style.map(
            "Tabela.Treeview.Heading",
            background=[("active", "#0D47A1")]
        )

        container = ttk.Frame(frame_externo)
        container.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            container,
            columns=self.colunas_chave,
            show="headings",
            style="Tabela.Treeview",
            selectmode="browse"
        )

        for c in self.colunas:
            self.tree.heading(
                c["chave"],
                text=c["rotulo"],
                command=lambda ch=c["chave"]: self._ordenar_por(ch)
            )
            self.tree.column(
                c["chave"],
                width=c.get("largura", 120),
                minwidth=60,
                anchor=c.get("alinhamento", "w")
            )

        self.tree.grid(row=0, column=0, sticky="nsew")

        scroll_v = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        scroll_v.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scroll_v.set)

        scroll_h = ttk.Scrollbar(container, orient="horizontal", command=self.tree.xview)
        scroll_h.grid(row=1, column=0, sticky="ew")
        self.tree.configure(xscrollcommand=scroll_h.set)

        self.label_mensagem = ctk.CTkLabel(
            container,
            text="",
            font=("Segoe UI", 15, "bold"),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="center",
            justify="center"
        )

    def _formatar_valor(self, chave, valor):
        formato = self.colunas_formato.get(chave)
        if formato == "moeda":
            if valor is None or (isinstance(valor, float) and valor != valor):
                return "R$ 0,00"
            s = f"R$ {valor:,.2f}"
            return s.replace(",", "X").replace(".", ",").replace("X", ".")
        elif formato == "data":
            if pd.isna(valor) or valor is None:
                return "---"
            if hasattr(valor, "strftime"):
                return valor.strftime("%d/%m/%Y")
            return str(valor).split(" ")[0]
        elif formato == "sim_nao":
            if valor is True or str(valor).lower() == "true":
                return "Sim"
            return "N\u00e3o"
        elif formato == "inteiro":
            if valor is None or (isinstance(valor, float) and valor != valor):
                return "0"
            return str(int(valor))
        else:
            if valor is None or (isinstance(valor, float) and valor != valor):
                return ""
            return str(valor)

    def carregar(self, dataframe):
        self.esconder_mensagem()

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.dados_originais = dataframe.copy() if dataframe is not None else None
        self.coluna_ordenada = None

        if dataframe is None or dataframe.empty:
            return

        for idx, linha in dataframe.iterrows():
            valores = []
            for chave in self.colunas_chave:
                valor_raw = linha.get(chave)
                valores.append(self._formatar_valor(chave, valor_raw))

            tag = "linha_par" if idx % 2 == 0 else "linha_impar"
            self.tree.insert("", "end", values=valores, tags=(tag,))

        self.tree.tag_configure("linha_par", background=COR_LINHA_1)
        self.tree.tag_configure("linha_impar", background=COR_LINHA_2)

    def _ordenar_por(self, coluna_chave):
        if self.dados_originais is None or self.dados_originais.empty:
            return

        if self.coluna_ordenada == coluna_chave:
            self.coluna_ordenada = None
            self.carregar(self.dados_originais)
            for c in self.colunas:
                self.tree.heading(c["chave"], text=c["rotulo"])
            return

        self.coluna_ordenada = coluna_chave

        dados_ordenados = self.dados_originais.copy()

        formato = self.colunas_formato.get(coluna_chave)
        if formato == "moeda":
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False, key=lambda x: x.fillna(0))
        elif formato == "sim_nao":
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False)
        else:
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False, na_position="last")

        self.carregar(dados_ordenados)

        for c in self.colunas:
            texto = c["rotulo"]
            if c["chave"] == coluna_chave:
                texto += " \u25BC"
            self.tree.heading(c["chave"], text=texto)

    def mostrar_mensagem(self, texto):
        self.limpar()
        self.label_mensagem.configure(text=texto)
        self.label_mensagem.grid(row=0, column=0, sticky="nsew")

    def esconder_mensagem(self):
        self.label_mensagem.grid_forget()

    def limpar(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.dados_originais = None
        self.esconder_mensagem()
