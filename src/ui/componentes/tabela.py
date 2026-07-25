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
        self.coluna_ativa = None

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
            selectmode="extended"
        )

        self.tree.bind("<Button-1>", self._definir_coluna_ativa, add="+")
        self.tree.bind("<B1-Motion>", self._estender_selecao, add="+")
        self.tree.bind("<Control-a>", self._selecionar_tudo)
        self.tree.bind("<Control-A>", self._selecionar_tudo)
        self.after(0, lambda: self.winfo_toplevel().bind("<Control-c>", self._copiar_selecao))
        self.after(0, lambda: self.winfo_toplevel().bind("<Control-C>", self._copiar_selecao))

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
        elif formato == "numero":
            if valor is None or (isinstance(valor, float) and valor != valor):
                return "0"
            return f"{int(valor):,}".replace(",", ".")
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
        self.coluna_ativa = None

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

        dados_originais = self.dados_originais
        dados_ordenados = dados_originais.copy()

        formato = self.colunas_formato.get(coluna_chave)
        if formato == "moeda":
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False, key=lambda x: x.fillna(0))
        elif formato == "sim_nao":
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False)
        else:
            dados_ordenados = dados_ordenados.sort_values(coluna_chave, ascending=False, na_position="last")

        self.carregar(dados_ordenados)
        self.dados_originais = dados_originais
        self.coluna_ordenada = coluna_chave

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
        self.coluna_ativa = None
        self.esconder_mensagem()

    def _definir_coluna_ativa(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col_id = self.tree.identify_column(event.x)
        if not col_id:
            return
        try:
            col_index = int(col_id.replace("#", "")) - 1
            if 0 <= col_index < len(self.colunas_chave):
                self.coluna_ativa = self.colunas_chave[col_index]
        except ValueError:
            pass

    def _estender_selecao(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            return
        items = self.tree.get_children()
        if row_id not in items:
            return
        focus_id = self.tree.focus()
        if not focus_id or focus_id not in items:
            self.tree.selection_set([row_id])
            return
        start = min(items.index(focus_id), items.index(row_id))
        end = max(items.index(focus_id), items.index(row_id))
        self.tree.selection_set(list(items[start:end + 1]))

    def _selecionar_tudo(self, event):
        items = self.tree.get_children()
        if items:
            self.tree.selection_set(items)
        return "break"

    def _copiar_selecao(self, event):
        items = self.tree.selection()
        if not items or not self.coluna_ativa:
            return
        col_index = self.colunas_chave.index(self.coluna_ativa)
        linhas = []
        for item in items:
            valores = self.tree.item(item, "values")
            if col_index < len(valores):
                linhas.append(str(valores[col_index]))
        texto = "\n".join(linhas)
        if texto:
            self.winfo_toplevel().clipboard_clear()
            self.winfo_toplevel().clipboard_append(texto)
