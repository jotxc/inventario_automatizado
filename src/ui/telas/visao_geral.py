import threading
import pandas as pd
import customtkinter as ctk

from ui.tema import (
    COR_PRIMARIA, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA, COR_SUCESSO, COR_AVISO, COR_ERRO
)
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.rodape import Rodape


class CartaoTipoDeposito(ctk.CTkFrame):

    def __init__(self, master, dados, **kwargs):
        super().__init__(
            master,
            fg_color=COR_CARD,
            border_color=COR_BORDA,
            border_width=1,
            corner_radius=10,
            **kwargs
        )

        self.grid_columnconfigure(0, weight=1)

        tipo = dados["tipo_deposito"]
        total_lotes = int(dados["total_lotes"])
        lotes_nunca = int(dados["lotes_nunca_contados"])
        pct_primeira = dados["percentual_primeira_contagem"]
        valor_total = dados["valor_pendente"]
        valor_prim = dados["valor_pendente_primeira_contagem"]
        media_dias = int(round(dados["media_dias_sem_contagem"])) if pd.notna(dados["media_dias_sem_contagem"]) else 0
        max_dias = int(dados["max_dias_sem_contagem"]) if pd.notna(dados["max_dias_sem_contagem"]) else 0

        if pct_primeira >= 60:
            cor_critica = COR_ERRO
        elif pct_primeira >= 30:
            cor_critica = COR_AVISO
        else:
            cor_critica = COR_SUCESSO

        label_titulo = ctk.CTkLabel(
            self,
            text=f"Tipo de Dep\u00f3sito: {tipo}",
            font=("Segoe UI", 16, "bold"),
            text_color=COR_PRIMARIA,
            anchor="w"
        )
        label_titulo.grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        frame_barra = ctk.CTkFrame(self, fg_color="transparent")
        frame_barra.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="ew")
        frame_barra.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkProgressBar(
            frame_barra,
            width=200,
            height=12,
            corner_radius=6,
            fg_color=COR_BORDA,
            progress_color=cor_critica
        )
        barra.grid(row=0, column=0, sticky="ew")
        barra.set(pct_primeira / 100)

        label_pct = ctk.CTkLabel(
            frame_barra,
            text=f"{pct_primeira:.0f}% 1\u00aa Contagem",
            font=("Segoe UI", 12, "bold"),
            text_color=cor_critica
        )
        label_pct.grid(row=0, column=1, padx=(10, 0))

        frame_metricas = ctk.CTkFrame(self, fg_color="transparent")
        frame_metricas.grid(row=2, column=0, padx=20, pady=(5, 18), sticky="ew")
        frame_metricas.grid_columnconfigure(0, weight=1)
        frame_metricas.grid_columnconfigure(1, weight=1)

        metrica_esquerda = [
            ("Lotes Eleg\u00edveis", str(total_lotes)),
            ("Lotes Nunca Contados", str(lotes_nunca)),
        ]
        metrica_direita = [
            ("M\u00e9dia Dias s/ Contagem", f"{media_dias} dias"),
            ("M\u00e1x Dias s/ Contagem", f"{max_dias} dias"),
        ]

        for i, (rotulo, valor) in enumerate(metrica_esquerda):
            frame_item = ctk.CTkFrame(frame_metricas, fg_color="transparent")
            frame_item.grid(row=i, column=0, sticky="ew", pady=2)
            frame_item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                frame_item,
                text=rotulo,
                font=("Segoe UI", 11),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w"
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                frame_item,
                text=valor,
                font=("Segoe UI", 12, "bold"),
                text_color=COR_TEXTO,
                anchor="e"
            ).grid(row=0, column=1, sticky="e")

        for i, (rotulo, valor) in enumerate(metrica_direita):
            frame_item = ctk.CTkFrame(frame_metricas, fg_color="transparent")
            frame_item.grid(row=i, column=1, sticky="ew", pady=2)
            frame_item.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                frame_item,
                text=rotulo,
                font=("Segoe UI", 11),
                text_color=COR_TEXTO_SECUNDARIO,
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=(20, 0))

            ctk.CTkLabel(
                frame_item,
                text=valor,
                font=("Segoe UI", 12, "bold"),
                text_color=COR_TEXTO,
                anchor="e"
            ).grid(row=0, column=1, sticky="e")

        linha_valor = ctk.CTkFrame(self, fg_color=COR_BORDA, height=1)
        linha_valor.grid(row=3, column=0, padx=20, sticky="ew")

        frame_valores = ctk.CTkFrame(self, fg_color="transparent")
        frame_valores.grid(row=4, column=0, padx=20, pady=(10, 18), sticky="ew")
        frame_valores.grid_columnconfigure(0, weight=1)
        frame_valores.grid_columnconfigure(1, weight=1)

        valor_total_fmt = self._formatar_moeda(valor_total)
        valor_prim_fmt = self._formatar_moeda(valor_prim)

        ctk.CTkLabel(
            frame_valores,
            text="Valor Pendente Total",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            frame_valores,
            text=valor_total_fmt,
            font=("Segoe UI", 14, "bold"),
            text_color=COR_TEXTO,
            anchor="w"
        ).grid(row=1, column=0, sticky="w")

        ctk.CTkLabel(
            frame_valores,
            text="Valor Pendente (1\u00aa Cont.)",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        ).grid(row=0, column=1, sticky="w", padx=(20, 0))

        ctk.CTkLabel(
            frame_valores,
            text=valor_prim_fmt,
            font=("Segoe UI", 14, "bold"),
            text_color=cor_critica,
            anchor="w"
        ).grid(row=1, column=1, sticky="w", padx=(20, 0))

    @staticmethod
    def _formatar_moeda(valor):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


class TelaVisaoGeral(ctk.CTkFrame):

    def __init__(self, master, controller, ao_voltar=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.controller = controller
        self.ao_voltar = ao_voltar

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.cabecalho = Cabecalho(
            self,
            titulo="GERADOR DE INVENT\u00c1RIO",
            subtitulo="Vis\u00e3o Geral por Tipo de Dep\u00f3sito"
        )
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        frame_botao = ctk.CTkFrame(self, fg_color="transparent")
        frame_botao.grid(row=1, column=0, sticky="ew", padx=40, pady=(15, 5))
        frame_botao.grid_columnconfigure(1, weight=1)

        self.botao_voltar = ctk.CTkButton(
            frame_botao,
            text="\u2190  VOLTAR",
            font=("Segoe UI", 13, "bold"),
            command=self._voltar,
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_PRIMARIA,
            hover_color=COR_BORDA,
            border_color=COR_PRIMARIA,
            border_width=2,
            height=38,
            width=140,
            corner_radius=8
        )
        self.botao_voltar.grid(row=0, column=0, padx=(0, 15), pady=5, sticky="w")

        self.botao_atualizar = ctk.CTkButton(
            frame_botao,
            text="\U0001F504  Atualizar",
            font=("Segoe UI", 13),
            command=self._carregar_dados,
            fg_color=COR_PRIMARIA,
            hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO,
            height=38,
            width=130,
            corner_radius=8
        )
        self.botao_atualizar.grid(row=0, column=1, padx=0, pady=5, sticky="w")

        self.label_loading = ctk.CTkLabel(
            frame_botao,
            text="",
            font=("Segoe UI", 12),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        )
        self.label_loading.grid(row=0, column=2, padx=(10, 0), pady=5, sticky="w")

        self.frame_cards = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.frame_cards.grid(row=2, column=0, sticky="nsew", padx=40, pady=(5, 15))
        self.frame_cards.grid_columnconfigure(0, weight=1)

        self.rodape = Rodape(self)
        self.rodape.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 15))

        self._carregar_dados()

    def _carregar_dados(self):
        self._limpar_cards()
        self.label_loading.configure(text="Calculando...")
        self.botao_atualizar.configure(state="disabled")
        self.botao_voltar.configure(state="disabled")

        threading.Thread(target=self._executar_carga, daemon=True).start()

    def _executar_carga(self):
        try:
            visao = self.controller.obter_visao_geral()
            self.after(0, lambda: self._pos_carga(visao))
        except Exception as e:
            self.after(0, lambda: self._erro_carga(str(e)))

    def _pos_carga(self, visao):
        self.label_loading.configure(text="")
        self.botao_atualizar.configure(state="normal")
        self.botao_voltar.configure(state="normal")

        if visao is None or visao.empty:
            mensagem = ctk.CTkLabel(
                self.frame_cards,
                text="Nenhum dado dispon\u00edvel. Importe os arquivos primeiro.",
                font=("Segoe UI", 14),
                text_color=COR_TEXTO_SECUNDARIO
            )
            mensagem.grid(row=0, column=0, padx=20, pady=30)
            self.rodape.atualizar("Sem dados para exibir")
            return

        visao = visao.sort_values("percentual_primeira_contagem", ascending=False)

        for idx, (_, row) in enumerate(visao.iterrows()):
            card = CartaoTipoDeposito(self.frame_cards, row)
            card.grid(row=idx, column=0, sticky="ew", padx=0, pady=(0, 15))

        total_tipos = len(visao)
        total_lotes = int(visao["total_lotes"].sum())
        self.rodape.atualizar(
            f"{total_tipos} tipo(s) de dep\u00f3sito, {total_lotes} lote(s) eleg\u00edveis"
        )

    def _erro_carga(self, erro):
        self.label_loading.configure(text="")
        self.botao_atualizar.configure(state="normal")
        self.botao_voltar.configure(state="normal")

        mensagem = ctk.CTkLabel(
            self.frame_cards,
            text=f"Erro ao carregar dados:\n{erro}",
            font=("Segoe UI", 14),
            text_color=COR_ERRO
        )
        mensagem.grid(row=0, column=0, padx=20, pady=30)
        self.rodape.atualizar(f"Erro: {erro}")

    def _limpar_cards(self):
        for widget in self.frame_cards.winfo_children():
            widget.destroy()

    def _voltar(self):
        if self.ao_voltar:
            self.ao_voltar()
