from datetime import datetime
import os
import platform
import subprocess
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox

from config.config import ARQUIVO_HISTORICO
from ui.tema import (
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA, COR_SUCESSO, COR_SUCESSO_HOVER, COR_AVISO, COR_ERRO, COR_ERRO_HOVER
)
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.tabela import TabelaDados


COR_PENDENTE = "#F57F17"
COR_PENDENTE_FUNDO = "#FFF8E1"


def _formatar_moeda(valor):
    try:
        s = f"R$ {float(valor):,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"


def _limpar_valor(valor):
    if isinstance(valor, float) and pd.isna(valor):
        return ""
    if isinstance(valor, float) and valor == int(valor):
        return str(int(valor))
    return str(valor).strip()


def _formatar_data(valor):
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    if isinstance(valor, str) and valor:
        try:
            dt = datetime.fromisoformat(valor)
            return dt.strftime("%d/%m/%Y %H:%M")
        except (ValueError, TypeError):
            return valor
    return "---"


COLUNAS_DETALHES = [
    {"chave": "material", "rotulo": "Material", "largura": 100, "alinhamento": "w", "formato": "inteiro"},
    {"chave": "lote", "rotulo": "Lote", "largura": 100, "alinhamento": "w"},
    {"chave": "tipo_deposito", "rotulo": "Tipo Dep.", "largura": 90, "alinhamento": "center"},
    {"chave": "quantidade_posicoes", "rotulo": "Posi\u00e7\u00f5es", "largura": 90, "alinhamento": "center", "formato": "inteiro"},
    {"chave": "valor_lote", "rotulo": "Valor Lote", "largura": 130, "alinhamento": "e", "formato": "moeda"},
    {"chave": "documento", "rotulo": "Documento", "largura": 130, "alinhamento": "w"},
]


class TelaHistorico(ctk.CTkFrame):

    def __init__(self, master, controller, ao_voltar=None, ao_visualizar_geracao=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.controller = controller
        self.ao_voltar = ao_voltar
        self.ao_visualizar_geracao = ao_visualizar_geracao

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.cabecalho = Cabecalho(
            self,
            titulo="HIST\u00d3RICO DE DOCUMENTOS",
            subtitulo="Visualize, edite e gerencie todas as gera\u00e7\u00f5es de documentos"
        )
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        self._criar_barra_busca()
        self._criar_area_cards()
        self._criar_rodape()

        self.geracoes = None
        self.cards = {}
        self._after_id = None
        self._busca_after_id = None

        self.after(0, self._carregar_dados)

    def _criar_barra_busca(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=40, pady=(12, 6))
        frame.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(frame, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_columnconfigure(1, weight=1)

        label_busca = ctk.CTkLabel(
            barra, text="\U0001F50D", font=("Segoe UI", 16), text_color=COR_TEXTO_SECUNDARIO
        )
        label_busca.grid(row=0, column=0, padx=(15, 5), pady=8)

        self.entry_busca = ctk.CTkEntry(
            barra,
            placeholder_text="Buscar por data, material, lote, documento...",
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO,
            font=("Segoe UI", 12)
        )
        self.entry_busca.grid(row=0, column=1, padx=(5, 10), pady=8, sticky="ew")
        self.entry_busca.bind("<KeyRelease>", self._agendar_busca)

        self.label_total = ctk.CTkLabel(
            barra, text="", font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO
        )
        self.label_total.grid(row=0, column=2, padx=(5, 15), pady=8)

        self.botao_voltar = ctk.CTkButton(
            barra,
            text="\u2190  VOLTAR",
            font=("Segoe UI", 12, "bold"),
            command=self._voltar,
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_PRIMARIA,
            hover_color=COR_BORDA,
            border_color=COR_PRIMARIA,
            border_width=2,
            height=30,
            width=100,
            corner_radius=8
        )
        self.botao_voltar.grid(row=0, column=3, padx=(0, 12), pady=8)

    def _criar_area_cards(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=2, column=0, sticky="nsew", padx=40, pady=(2, 2))
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.scroll = ctk.CTkScrollableFrame(
            container, fg_color="transparent", corner_radius=0
        )
        self.scroll.grid(row=0, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def _criar_rodape(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", padx=40, pady=(2, 10))
        frame.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(frame, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_columnconfigure(0, weight=1)

        self.label_rodape = ctk.CTkLabel(
            barra, text="", font=("Segoe UI", 12), text_color=COR_TEXTO_SECUNDARIO
        )
        self.label_rodape.grid(row=0, column=0, padx=(15, 10), pady=8, sticky="w")

        self.botao_abrir_excel = ctk.CTkButton(
            barra,
            text="\U0001F4C4  Abrir Excel",
            font=("Segoe UI", 12),
            command=self._abrir_excel,
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
            text_color=COR_TEXTO_BRANCO,
            height=30,
            width=130,
            corner_radius=8
        )
        self.botao_abrir_excel.grid(row=0, column=1, padx=(0, 12), pady=8)

    def _agendar_busca(self, event=None):
        if self._busca_after_id:
            self.after_cancel(self._busca_after_id)
        self._busca_after_id = self.after(300, self._filtrar_cards)

    def _carregar_dados(self):
        try:
            self.geracoes = self.controller.listar_geracoes_historico()
            self.after(0, self._renderizar)
        except Exception as e:
            self.after(0, lambda: self._erro(str(e)))

    def _erro(self, erro):
        messagebox.showerror("Erro", f"Erro ao carregar hist\u00f3rico:\n{erro}")

    def _renderizar(self):
        for w in self.scroll.winfo_children():
            w.destroy()
        self.cards.clear()

        if self.geracoes is None or self.geracoes.empty:
            label = ctk.CTkLabel(
                self.scroll,
                text="Nenhum hist\u00f3rico encontrado.\n\nGere um documento para criar o hist\u00f3rico.",
                font=("Segoe UI", 16, "bold"),
                text_color=COR_TEXTO_SECUNDARIO,
                justify="center"
            )
            label.grid(row=0, column=0, pady=80)
            self.label_total.configure(text="0 gera\u00e7\u00f5es")
            self.label_rodape.configure(text="Nenhum registro no hist\u00f3rico.")
            return

        for idx, (_, row) in enumerate(self.geracoes.iterrows()):
            card = _CardGeracao(
                self.scroll,
                dados=row,
                ao_editar=self._editar_documento,
                ao_excluir=self._excluir_geracao,
                ao_visualizar=self._visualizar_geracao,
            )
            card.grid(row=idx, column=0, sticky="ew", pady=(0, 6))
            self.cards[row["id_geracao"]] = card

        total = len(self.geracoes)
        self.label_total.configure(text=f"{total} gera\u00e7\u00e3o(\u00f5es)")

        total_lotes = int(self.geracoes["total_lotes_geracao"].sum()) if "total_lotes_geracao" in self.geracoes.columns else 0
        self.label_rodape.configure(
            text=f"Total: {total} gera\u00e7\u00f5es, {total_lotes} lotes no hist\u00f3rico"
        )

    def _filtrar_cards(self, event=None):
        texto = self.entry_busca.get().strip().lower()
        visiveis = 0

        for id_ger, card in self.cards.items():
            if not texto:
                card.grid()
                visiveis += 1
            else:
                if card.corresponde(texto):
                    card.grid()
                    visiveis += 1
                else:
                    card.grid_remove()

        total = len(self.cards)
        self.label_total.configure(
            text=f"{visiveis} de {total} gera\u00e7\u00e3o(\u00f5es)" if texto else f"{total} gera\u00e7\u00e3o(\u00f5es)"
        )

    def _editar_documento(self, id_geracao, dados):
        dialogo = ctk.CTkInputDialog(
            title="Editar N\u00famero do Documento",
            text="Digite o n\u00famero do documento SAP:"
        )
        numero = dialogo.get_input()
        if not numero or not numero.strip():
            return

        sucesso, mensagem = self.controller.atualizar_numero_documento(id_geracao, numero.strip())
        if sucesso:
            if id_geracao in self.cards:
                self.cards[id_geracao].atualizar_documento(numero.strip())
            messagebox.showinfo("Sucesso", f"Documento n\u00ba {numero.strip()} salvo!")
        else:
            messagebox.showerror("Erro", mensagem)

    def _excluir_geracao(self, id_geracao, dados):
        data = _formatar_data(dados.get("data_geracao"))
        if not messagebox.askyesno(
            "Confirmar Exclus\u00e3o",
            f"Tem certeza que deseja excluir a gera\u00e7\u00e3o do dia {data}?\n\n"
            f"Esta a\u00e7\u00e3o n\u00e3o pode ser desfeita."
        ):
            return

        sucesso = self.controller.excluir_geracao_historico(id_geracao)
        if sucesso:
            if id_geracao in self.cards:
                self.cards[id_geracao].destroy()
                del self.cards[id_geracao]
            self._atualizar_contadores()
            messagebox.showinfo("Sucesso", "Gera\u00e7\u00e3o exclu\u00edda do hist\u00f3rico.")
        else:
            messagebox.showerror("Erro", "N\u00e3o foi poss\u00edvel excluir a gera\u00e7\u00e3o.")

    def _visualizar_geracao(self, id_geracao, dados):
        if self.ao_visualizar_geracao:
            from historico.historico_documentos import carregar_ultima_geracao
            ultimo = carregar_ultima_geracao()
            if ultimo is not None:
                self.ao_visualizar_geracao(ultimo)
            else:
                messagebox.showwarning("Aviso", "N\u00e3o foi poss\u00edvel carregar a gera\u00e7\u00e3o.")

    def _atualizar_contadores(self):
        total = len(self.cards)
        self.label_total.configure(text=f"{total} gera\u00e7\u00e3o(\u00f5es)")
        self.label_rodape.configure(
            text=f"Total: {total} gera\u00e7\u00f5es no hist\u00f3rico"
        )

    def _abrir_excel(self):
        if not os.path.exists(ARQUIVO_HISTORICO):
            messagebox.showwarning("Hist\u00f3rico", "Arquivo de hist\u00f3rico n\u00e3o encontrado.")
            return
        if platform.system() == "Windows":
            os.startfile(ARQUIVO_HISTORICO)
        else:
            subprocess.call(["open", ARQUIVO_HISTORICO])

    def _voltar(self):
        if self.ao_voltar:
            self.ao_voltar()


class _CardGeracao(ctk.CTkFrame):

    def __init__(self, master, dados, ao_editar=None, ao_excluir=None, ao_visualizar=None):
        super().__init__(master, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=10)
        self.dados = dados
        self.ao_editar = ao_editar
        self.ao_excluir = ao_excluir
        self.ao_visualizar = ao_visualizar

        self.expandido = False
        self.frame_detalhes = None
        self.id_geracao = str(dados.get("id_geracao", ""))
        self.botao_expandir = None
        self.label_documento = None

        self.grid_columnconfigure(0, weight=1)

        self._criar_linha_principal()
        self._criar_linha_stats()
        self._criar_area_expansao()

    def _criar_linha_principal(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=0, column=0, sticky="ew", padx=18, pady=(10, 2))
        frame.grid_columnconfigure(3, weight=1)

        col = 0

        documento = _limpar_valor(self.dados.get("documento", ""))
        if documento:
            self.label_documento = ctk.CTkLabel(
                frame,
                text=f"\U0001F511  N\u00ba Doc.: {documento}",
                font=("Segoe UI", 14, "bold"),
                text_color=COR_SUCESSO
            )
        else:
            self.label_documento = ctk.CTkLabel(
                frame,
                text="\U0001F512  N\u00ba Doc.: Pendente",
                font=("Segoe UI", 14, "bold"),
                text_color=COR_PENDENTE
            )
        self.label_documento.grid(row=0, column=col, padx=(0, 18), sticky="w")
        col += 1

        data_raw = self.dados.get("data_geracao", "")
        data_str = _formatar_data(data_raw)
        ctk.CTkLabel(
            frame,
            text=f"\U0001F4C5  {data_str}",
            font=("Segoe UI", 13),
            text_color=COR_TEXTO_SECUNDARIO
        ).grid(row=0, column=col, padx=(0, 18), sticky="w")
        col += 1

        tipo_dep = _limpar_valor(self.dados.get("tipo_deposito", ""))
        if tipo_dep:
            badge_tipo = ctk.CTkLabel(
                frame,
                text=f"  \U0001F3ED Dep\u00f3sito {tipo_dep}  ",
                font=("Segoe UI", 12, "bold"),
                text_color=COR_TEXTO_BRANCO,
                fg_color=COR_PRIMARIA,
                corner_radius=4
            )
            badge_tipo.grid(row=0, column=col, padx=(0, 10), sticky="w")
            col += 1

        frame_botoes = ctk.CTkFrame(frame, fg_color="transparent")
        frame_botoes.grid(row=0, column=col, padx=(0, 0), sticky="e")

        botoes = [
            ("Editar", "\u270F", COR_AVISO, None, lambda: self._editar()),
            ("Excluir", "\U0001F5D1", COR_ERRO, COR_ERRO_HOVER, lambda: self._excluir()),
            ("Ver", "\U0001F441", COR_PRIMARIA, COR_PRIMARIA_HOVER, lambda: self._visualizar()),
            ("Expandir" if not self.expandido else "Recolher", "\u25BC" if not self.expandido else "\u25B2", COR_TEXTO_SECUNDARIO, COR_BORDA, lambda: self._toggle_expandir()),
        ]

        for i, (rotulo, icone, cor_bg, cor_hv, comando) in enumerate(botoes):
            btn = ctk.CTkButton(
                frame_botoes,
                text=f"{icone}  {rotulo}",
                font=("Segoe UI", 11, "bold"),
                command=comando,
                fg_color=cor_bg,
                hover_color=cor_hv if cor_hv else cor_bg,
                text_color=COR_TEXTO_BRANCO,
                height=28,
                width=90,
                corner_radius=6
            )
            btn.grid(row=0, column=i, padx=3)
            if rotulo == "Expandir" or rotulo == "Recolher":
                self.botao_expandir = btn

    def _criar_linha_stats(self):
        frame = ctk.CTkFrame(self, fg_color=COR_FUNDO, corner_radius=6)
        frame.grid(row=1, column=0, sticky="ew", padx=18, pady=(2, 10))

        total_lotes = int(self.dados.get("total_lotes_geracao", 0))
        total_posicoes = int(self.dados.get("total_posicoes_geracao", 0))
        total_valor = self.dados.get("total_valor_geracao", 0)

        stats = [
            ("\U0001F4E6", f"{total_lotes} lotes"),
            ("\U0001F4CD", f"{total_posicoes} posi\u00e7\u00f5es"),
            ("\U0001F4B0", _formatar_moeda(total_valor)),
        ]

        for i, (icone, texto) in enumerate(stats):
            ctk.CTkLabel(
                frame,
                text=f"{icone}  {texto}",
                font=("Segoe UI", 13, "bold"),
                text_color=COR_TEXTO
            ).grid(row=0, column=i, padx=(15, 15), pady=6, sticky="w")

    def _criar_area_expansao(self):
        self.frame_detalhes = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_detalhes.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.frame_detalhes.grid_columnconfigure(0, weight=1)
        self.frame_detalhes.grid_remove()

    def _editar(self):
        if self.ao_editar:
            self.ao_editar(self.id_geracao, self.dados)

    def _excluir(self):
        if self.ao_excluir:
            self.ao_excluir(self.id_geracao, self.dados)

    def _visualizar(self):
        if self.ao_visualizar:
            self.ao_visualizar(self.id_geracao, self.dados)

    def _toggle_expandir(self):
        if self.expandido:
            self._recolher()
        else:
            self._expandir()

    def _expandir(self):
        if self.expandido:
            return
        self.expandido = True

        for w in self.frame_detalhes.winfo_children():
            w.destroy()

        from historico.historico_documentos import carregar_historico_documentos
        try:
            historico = carregar_historico_documentos()
            if not historico.empty and "id_geracao" in historico.columns:
                historico["id_geracao"] = historico["id_geracao"].fillna("").astype(str)
                detalhes = historico[historico["id_geracao"] == self.id_geracao].copy()

                if not detalhes.empty:
                    cols_disp = [c["chave"] for c in COLUNAS_DETALHES if c["chave"] in detalhes.columns]
                    if cols_disp:
                        detalhes = detalhes[cols_disp]

                    tabela = TabelaDados(self.frame_detalhes, COLUNAS_DETALHES)
                    tabela.grid(row=0, column=0, sticky="nsew")
                    tabela.carregar(detalhes)
        except Exception as e:
            label_erro = ctk.CTkLabel(
                self.frame_detalhes,
                text=f"Erro ao carregar detalhes: {e}",
                text_color=COR_ERRO
            )
            label_erro.grid(row=0, column=0)

        self.frame_detalhes.grid()

        self._reconfigurar_botao_expandir()

    def _recolher(self):
        if not self.expandido:
            return
        self.expandido = False
        self.frame_detalhes.grid_remove()
        self._reconfigurar_botao_expandir()

    def _reconfigurar_botao_expandir(self):
        if self.botao_expandir:
            self.botao_expandir.configure(
                text="\u25B2  Recolher" if self.expandido else "\u25BC  Expandir"
            )

    def atualizar_documento(self, numero):
        self.dados["documento"] = numero
        if self.label_documento:
            self.label_documento.configure(
                text=f"\U0001F511  N\u00ba Doc.: {numero}",
                text_color=COR_SUCESSO
            )

    def corresponde(self, texto):
        if not texto:
            return True
        data_str = _formatar_data(self.dados.get("data_geracao", "")).lower()
        tipo_dep = _limpar_valor(self.dados.get("tipo_deposito", "")).lower()
        documento = _limpar_valor(self.dados.get("documento", "")).lower()
        total_lotes = str(self.dados.get("total_lotes_geracao", ""))
        return any(texto in v for v in [data_str, tipo_dep, documento, total_lotes])
