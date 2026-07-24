import os
import platform
import subprocess
import customtkinter as ctk
from tkinter import messagebox

from config.config import ARQUIVO_SAIDA, ARQUIVO_HISTORICO
from ui.tema import (
    COR_PRIMARIA, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA
)
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.resumo import Resumo


class TelaResultado(ctk.CTkFrame):

    def __init__(self, master, resultado, ao_voltar=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.resultado = resultado
        self.ao_voltar = ao_voltar

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.cabecalho = Cabecalho(
            self,
            titulo="GERADOR DE INVENT\u00c1RIO",
            subtitulo="Documento gerado com sucesso"
        )
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        frame_meio = ctk.CTkFrame(self, fg_color="transparent")
        frame_meio.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        frame_meio.grid_columnconfigure(0, weight=1)
        frame_meio.grid_rowconfigure(0, weight=1)

        card_container = ctk.CTkFrame(frame_meio, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=12)
        card_container.grid(row=0, column=0, sticky="nsew", ipadx=30, ipady=20)
        card_container.grid_columnconfigure(0, weight=1)

        sugestao = resultado["sugestao"]
        dados = {
            "criterio": resultado.get("criterio", ""),
            "tipo_deposito": resultado.get("tipo_deposito", ""),
            "lotes": len(sugestao),
            "posicoes": int(sugestao["quantidade_posicoes"].sum()),
            "valor": sugestao["valor_lote"].sum(),
            "arquivo": resultado.get("arquivo", "Documento_Inventario.xlsx")
        }

        titulo = ctk.CTkLabel(
            card_container,
            text="Resumo da Execu\u00e7\u00e3o",
            font=("Segoe UI", 22, "bold"),
            text_color=COR_PRIMARIA
        )
        titulo.grid(row=0, column=0, pady=(20, 25))

        frame_cartoes = ctk.CTkFrame(card_container, fg_color="transparent")
        frame_cartoes.grid(row=1, column=0, padx=40, sticky="ew")
        frame_cartoes.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._criar_cartao(frame_cartoes, "\U0001F4E6", "Lotes", str(dados["lotes"]), 0)
        self._criar_cartao(frame_cartoes, "\U0001F4CD", "Posi\u00e7\u00f5es", str(dados["posicoes"]), 1)
        valor_formatado = f"R$ {dados['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self._criar_cartao(frame_cartoes, "\U0001F4B0", "Valor Total", valor_formatado, 2)
        self._criar_cartao(frame_cartoes, "\U0001F4C4", "Arquivo", dados["arquivo"], 3)

        frame_botoes = ctk.CTkFrame(card_container, fg_color="transparent")
        frame_botoes.grid(row=2, column=0, pady=(30, 10))
        frame_botoes.grid_columnconfigure((0, 1, 2), weight=1)

        self.botao_documento = ctk.CTkButton(
            frame_botoes,
            text="\U0001F4C4  Abrir Documento",
            font=("Segoe UI", 14, "bold"),
            command=self.abrir_documento,
            fg_color=COR_PRIMARIA,
            hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO,
            height=45,
            width=200,
            corner_radius=8
        )
        self.botao_documento.grid(row=0, column=0, padx=10, pady=10)

        self.botao_historico = ctk.CTkButton(
            frame_botoes,
            text="\U0001F4CB  Abrir Hist\u00f3rico",
            font=("Segoe UI", 14, "bold"),
            command=self.abrir_historico,
            fg_color=COR_PRIMARIA,
            hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO,
            height=45,
            width=200,
            corner_radius=8
        )
        self.botao_historico.grid(row=0, column=1, padx=10, pady=10)

        self.botao_voltar = ctk.CTkButton(
            frame_botoes,
            text="\u2190  VOLTAR",
            font=("Segoe UI", 14, "bold"),
            command=self._voltar,
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_PRIMARIA,
            hover_color=COR_BORDA,
            border_color=COR_PRIMARIA,
            border_width=2,
            height=45,
            width=200,
            corner_radius=8
        )
        self.botao_voltar.grid(row=0, column=2, padx=10, pady=10)

        self.label_rodape = ctk.CTkLabel(
            card_container,
            text="Documento gerado com sucesso.",
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="center"
        )
        self.label_rodape.grid(row=3, column=0, pady=(10, 25))

    def _criar_cartao(self, parent, icone, rotulo, valor, coluna):
        card = ctk.CTkFrame(parent, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        card.grid(row=0, column=coluna, padx=8, pady=5, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        label_icone = ctk.CTkLabel(
            card,
            text=icone,
            font=("Segoe UI", 28),
            text_color=COR_TEXTO
        )
        label_icone.grid(row=0, column=0, pady=(15, 2))

        label_valor = ctk.CTkLabel(
            card,
            text=valor,
            font=("Segoe UI", 18, "bold"),
            text_color=COR_TEXTO
        )
        label_valor.grid(row=1, column=0, pady=(2, 2))

        label_rotulo = ctk.CTkLabel(
            card,
            text=rotulo,
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO
        )
        label_rotulo.grid(row=2, column=0, pady=(0, 15))

    def abrir_documento(self):
        if not os.path.exists(ARQUIVO_SAIDA):
            messagebox.showwarning("Arquivo", "Nenhum documento foi gerado ainda.")
            return
        self._abrir_arquivo(ARQUIVO_SAIDA)

    def abrir_historico(self):
        if not os.path.exists(ARQUIVO_HISTORICO):
            messagebox.showwarning("Hist\u00f3rico", "Hist\u00f3rico n\u00e3o encontrado.")
            return
        self._abrir_arquivo(ARQUIVO_HISTORICO)

    @staticmethod
    def _abrir_arquivo(caminho):
        if platform.system() == "Windows":
            os.startfile(caminho)
        else:
            subprocess.call(["open", caminho])

    def _voltar(self):
        if self.ao_voltar:
            self.ao_voltar()
