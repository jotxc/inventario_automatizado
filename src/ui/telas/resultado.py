import os
import platform
import subprocess
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox

from config.config import ARQUIVO_SAIDA, ARQUIVO_HISTORICO
from ui.tema import (
    COR_PRIMARIA, COR_PRIMARIA_HOVER, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA, COR_SUCESSO, COR_SUCESSO_HOVER, COR_AVISO
)
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.resumo import Resumo

from historico.historico_documentos import atualizar_documento_geracao


def _limpar_documento(valor):
    if isinstance(valor, float) and pd.isna(valor):
        return ""
    return str(valor).strip()


class TelaResultado(ctk.CTkFrame):

    def __init__(self, master, resultado, ao_voltar=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.resultado = resultado
        self.ao_voltar = ao_voltar

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        do_historico = resultado.get("do_historico", False)
        sugestao = resultado.get("sugestao")

        if sugestao is not None and not sugestao.empty and "quantidade_posicoes" in sugestao.columns:
            total_lotes = len(sugestao)
            total_posicoes = int(sugestao["quantidade_posicoes"].sum())
            total_valor = sugestao["valor_lote"].sum() if "valor_lote" in sugestao.columns else 0
        else:
            total_lotes = resultado.get("total_lotes", 0)
            total_posicoes = resultado.get("total_posicoes", 0)
            total_valor = resultado.get("total_valor", 0)

        subtitulo = "Documento do Hist\u00f3rico"
        if do_historico:
            data_raw = resultado.get("data_geracao", "")
            if isinstance(data_raw, datetime):
                subtitulo = f"\u00daltimo Documento \u2014 Gerado em {data_raw.strftime('%d/%m/%Y %H:%M')}"
            elif data_raw:
                subtitulo = f"\u00daltimo Documento \u2014 Gerado em {data_raw}"
        else:
            subtitulo = "Documento gerado com sucesso"
            data_raw = resultado.get("data_geracao", "")
            if isinstance(data_raw, datetime):
                subtitulo = f"Documento gerado em {data_raw.strftime('%d/%m/%Y %H:%M')}"
            elif data_raw:
                subtitulo = f"Documento gerado em {data_raw}"

        self.cabecalho = Cabecalho(
            self,
            titulo="GERADOR DE INVENT\u00c1RIO",
            subtitulo=subtitulo
        )
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        frame_meio = ctk.CTkFrame(self, fg_color="transparent")
        frame_meio.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        frame_meio.grid_columnconfigure(0, weight=1)
        frame_meio.grid_rowconfigure(0, weight=1)

        card_container = ctk.CTkFrame(frame_meio, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=12)
        card_container.grid(row=0, column=0, sticky="nsew", ipadx=30, ipady=20)
        card_container.grid_columnconfigure(0, weight=1)

        self._dados = {
            "criterio": resultado.get("criterio", ""),
            "tipo_deposito": resultado.get("tipo_deposito", ""),
            "lotes": total_lotes,
            "posicoes": total_posicoes,
            "valor": total_valor,
            "arquivo": resultado.get("arquivo", "Documento_Inventario.xlsx")
        }

        titulo = ctk.CTkLabel(
            card_container,
            text="Resumo da Execu\u00e7\u00e3o",
            font=("Segoe UI", 22, "bold"),
            text_color=COR_PRIMARIA
        )
        titulo.grid(row=0, column=0, pady=(20, 25))

        self._frame_cartoes = ctk.CTkFrame(card_container, fg_color="transparent")
        self._frame_cartoes.grid(row=1, column=0, padx=40, sticky="ew")
        self._frame_cartoes.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self._documento_atual = _limpar_documento(resultado.get("documento", ""))

        self._montar_cartoes(self._documento_atual)

        frame_botoes = ctk.CTkFrame(card_container, fg_color="transparent")
        frame_botoes.grid(row=2, column=0, pady=(30, 10))
        frame_botoes.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.botao_documento = ctk.CTkButton(
            frame_botoes,
            text="\U0001F4C4  Abrir Documento",
            font=("Segoe UI", 14, "bold"),
            command=self.abrir_documento,
            fg_color=COR_PRIMARIA,
            hover_color=COR_PRIMARIA_HOVER,
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
            hover_color=COR_PRIMARIA_HOVER,
            text_color=COR_TEXTO_BRANCO,
            height=45,
            width=200,
            corner_radius=8
        )
        self.botao_historico.grid(row=0, column=1, padx=10, pady=10)

        self.id_geracao = resultado.get("id_geracao", "")
        if self.id_geracao:
            self.botao_editar_documento = ctk.CTkButton(
                frame_botoes,
                text="\u270F  Informar N\u00ba Documento",
                font=("Segoe UI", 14, "bold"),
                command=self._informar_numero_documento,
                fg_color=COR_SUCESSO,
                hover_color=COR_SUCESSO_HOVER,
                text_color=COR_TEXTO_BRANCO,
                height=45,
                width=220,
                corner_radius=8
            )
            self.botao_editar_documento.grid(row=0, column=2, padx=10, pady=10)

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
        self.botao_voltar.grid(row=0, column=3, padx=10, pady=10)

        self.label_rodape = ctk.CTkLabel(
            card_container,
            text=subtitulo,
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="center"
        )
        self.label_rodape.grid(row=3, column=0, pady=(10, 25))

    def _montar_cartoes(self, documento):
        for w in self._frame_cartoes.winfo_children():
            w.destroy()

        self._criar_cartao(self._frame_cartoes, "\U0001F4E6", "Lotes", str(self._dados["lotes"]), 0)
        self._criar_cartao(self._frame_cartoes, "\U0001F4CD", "Posi\u00e7\u00f5es", str(self._dados["posicoes"]), 1)
        valor_fmt = f"R$ {self._dados['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        self._criar_cartao(self._frame_cartoes, "\U0001F4B0", "Valor Total", valor_fmt, 2)

        if documento:
            self._criar_cartao(self._frame_cartoes, "\U0001F511", "N\u00ba Documento", documento, 3)
        else:
            self._criar_cartao(self._frame_cartoes, "\U0001F512", "N\u00ba Documento", "Pendente", 3)

        tipo_dep = self._dados.get("tipo_deposito", "")
        if tipo_dep:
            self._criar_cartao(self._frame_cartoes, "\U0001F3ED", "Tipo Dep.", str(tipo_dep), 4)

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

    def _informar_numero_documento(self):
        from historico.historico_documentos import carregar_historico_documentos

        try:
            historico = carregar_historico_documentos()
            if not historico.empty and "id_geracao" in historico.columns:
                historico["id_geracao"] = historico["id_geracao"].fillna("").astype(str)
                mask = historico["id_geracao"] == str(self.id_geracao)
                if mask.any():
                    val = historico.loc[mask, "documento"].iloc[0]
                    if pd.notna(val) and str(val).strip():
                        if not messagebox.askyesno(
                            "N\u00famero j\u00e1 existente",
                            f"J\u00e1 existe o n\u00famero \"{str(val).strip()}\" para este documento.\n\nDeseja substituir?"
                        ):
                            return
        except Exception as e:
            print(f"Erro ao verificar documento existente: {e}")

        dialogo = ctk.CTkInputDialog(
            title="Informar N\u00famero do Documento",
            text="Digite o n\u00famero do documento gerado no SAP:"
        )
        numero = dialogo.get_input()
        if not numero or not numero.strip():
            return

        try:
            sucesso = atualizar_documento_geracao(self.id_geracao, numero.strip())
            if sucesso:
                self._documento_atual = numero.strip()
                self._montar_cartoes(self._documento_atual)
                messagebox.showinfo(
                    "Documento Salvo",
                    f"Documento n\u00ba {numero.strip()} salvo com sucesso!"
                )
            else:
                messagebox.showerror(
                    "Erro",
                    "N\u00e3o foi poss\u00edvel salvar o n\u00famero.\n\n"
                    "O ID desta gera\u00e7\u00e3o n\u00e3o foi encontrado no arquivo de hist\u00f3rico.\n"
                    "Tente gerar um novo documento primeiro."
                )
        except Exception as e:
            messagebox.showerror(
                "Erro",
                f"Ocorreu um erro ao salvar:\n{e}"
            )

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
