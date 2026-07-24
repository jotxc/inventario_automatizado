import threading
import os
import shutil
import platform
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog

from config.config import CRITERIOS_UI, ENTRADA_DIR
from ui.tema import (
    COR_PRIMARIA, COR_SUCESSO, COR_SUCESSO_HOVER,
    COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA, COR_AVISO, COR_ERRO
)
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.tabela import TabelaDados
from ui.componentes.rodape import Rodape
from ui.componentes.filtro_coluna_popup import FiltroColunaPopup


COLUNAS_TABELA = [
    {"chave": "material", "rotulo": "Material", "largura": 100, "alinhamento": "w"},
    {"chave": "descricao_material", "rotulo": "Descri\u00e7\u00e3o", "largura": 220, "alinhamento": "w"},
    {"chave": "lote", "rotulo": "Lote", "largura": 100, "alinhamento": "w"},
    {"chave": "tipo_deposito", "rotulo": "Tipo Dep.", "largura": 90, "alinhamento": "center"},
    {"chave": "quantidade_posicoes", "rotulo": "Posi\u00e7\u00f5es", "largura": 90, "alinhamento": "center", "formato": "inteiro"},
    {"chave": "estoque_total", "rotulo": "Est. Total", "largura": 110, "alinhamento": "e"},
    {"chave": "valor_lote", "rotulo": "Valor Total", "largura": 130, "alinhamento": "e", "formato": "moeda"},
    {"chave": "dias_sem_contagem", "rotulo": "Dias s/ Cont.", "largura": 110, "alinhamento": "center", "formato": "inteiro"},
    {"chave": "ultima_contagem", "rotulo": "Data \u00dalt. Cont.", "largura": 130, "alinhamento": "center", "formato": "data"},
    {"chave": "nunca_contado", "rotulo": "1\u00aa Contagem?", "largura": 110, "alinhamento": "center", "formato": "sim_nao"},
]

CRITERIOS_SECUNDARIOS = [
    "Nenhum",
    "Primeira Contagem",
    "Dias sem Contagem",
    "Valor do Lote",
    "Menos Posi\u00e7\u00f5es"
]

CRITERIO_SECUNDARIO_MAP = {
    "Nenhum": None,
    "Primeira Contagem": "primeira_contagem",
    "Dias sem Contagem": "dias",
    "Valor do Lote": "valor",
    "Menos Posi\u00e7\u00f5es": "posicoes"
}


class TelaVisualizacaoEstoque(ctk.CTkFrame):

    def __init__(self, master, controller, ao_exibir_resultado=None):
        super().__init__(master, fg_color=COR_FUNDO)
        self.controller = controller
        self.ao_exibir_resultado = ao_exibir_resultado

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.cabecalho = Cabecalho(
            self,
            titulo="GERADOR DE INVENT\u00c1RIO",
            subtitulo="Visualize, edite e gere documentos de invent\u00e1rio"
        )
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        self.ultimo_modo_sem_maquina = True

        self._criar_filtros()
        self._criar_barra_exclusao()
        self._criar_tabela()
        self._criar_barra_acoes()
        self.rodape = Rodape(self)
        self.rodape.grid(row=5, column=0, sticky="ew", padx=40, pady=(0, 15))

        self.after(300, self._iniciar_carregamento)

    def _iniciar_carregamento(self):
        self.rodape.atualizar("Carregando dados...")
        self.rodape.mostrar_progresso()
        threading.Thread(target=self._carregar_dados, daemon=True).start()

    def _carregar_dados(self):
        try:
            tipos = self.controller.carregar()
            self.after(0, lambda: self._pos_carregamento(tipos))
        except Exception as e:
            self.after(0, lambda: self._erro(str(e)))

    def _pos_carregamento(self, tipos):
        self.rodape.esconder_progresso()
        self.combo_tipo.configure(values=tipos)
        if tipos:
            self.combo_tipo.set(tipos[0])
        self.botao_gerar.configure(state="normal")
        self.botao_importar.configure(state="normal")
        self._atualizar_status_exclusao()
        self._atualizar_botao_ver_documento()
        self.rodape.atualizar("Pronto")

    def _erro(self, erro):
        self.rodape.esconder_progresso()
        self.rodape.atualizar(f"Erro: {erro}")

    def _criar_filtros(self):
        frame_filtros = ctk.CTkFrame(self, fg_color="transparent")
        frame_filtros.grid(row=1, column=0, sticky="ew", padx=40, pady=(20, 5))
        frame_filtros.grid_columnconfigure(0, weight=1)

        linha = ctk.CTkFrame(frame_filtros, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        linha.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        for i in range(9):
            linha.grid_columnconfigure(i, weight=0)
        linha.grid_columnconfigure(8, weight=1)

        pad_x = (15, 5)
        pad_y = 13

        col = 0
        label_criterio = ctk.CTkLabel(linha, text="1\u00ba Crit\u00e9rio:", font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO)
        label_criterio.grid(row=0, column=col, padx=pad_x, pady=pad_y, sticky="w")
        col += 1

        self.combo_criterio = ctk.CTkComboBox(
            linha,
            values=[
                "Primeira Contagem",
                "Dias sem Contagem",
                "Valor do Lote",
                "Menos Posi\u00e7\u00f5es"
            ],
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_TEXTO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            dropdown_fg_color=COR_TEXTO_BRANCO,
            dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_PRIMARIA,
            width=170,
            state="readonly"
        )
        self.combo_criterio.set("Valor do Lote")
        self.combo_criterio.grid(row=0, column=col, padx=(0, 10), pady=pad_y, sticky="w")
        col += 1

        label_criterio2 = ctk.CTkLabel(linha, text="2\u00ba Crit\u00e9rio:", font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO)
        label_criterio2.grid(row=0, column=col, padx=pad_x, pady=pad_y, sticky="w")
        col += 1

        self.combo_criterio2 = ctk.CTkComboBox(
            linha,
            values=CRITERIOS_SECUNDARIOS,
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_TEXTO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            dropdown_fg_color=COR_TEXTO_BRANCO,
            dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_PRIMARIA,
            width=170,
            state="readonly"
        )
        self.combo_criterio2.set("Nenhum")
        self.combo_criterio2.grid(row=0, column=col, padx=(0, 10), pady=pad_y, sticky="w")
        col += 1

        label_tipo = ctk.CTkLabel(linha, text="Tipo Dep.:", font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO)
        label_tipo.grid(row=0, column=col, padx=pad_x, pady=pad_y, sticky="w")
        col += 1

        self.combo_tipo = ctk.CTkComboBox(
            linha,
            values=[],
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_TEXTO,
            border_color=COR_TEXTO_SECUNDARIO,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            dropdown_fg_color=COR_TEXTO_BRANCO,
            dropdown_text_color=COR_TEXTO,
            dropdown_hover_color=COR_PRIMARIA,
            width=100,
            state="readonly"
        )
        self.combo_tipo.grid(row=0, column=col, padx=(0, 10), pady=pad_y, sticky="w")
        col += 1

        label_limite = ctk.CTkLabel(linha, text="Lim.:", font=("Segoe UI", 12, "bold"), text_color=COR_TEXTO)
        label_limite.grid(row=0, column=col, padx=pad_x, pady=pad_y, sticky="w")
        col += 1

        self.entry_limite = ctk.CTkEntry(
            linha,
            placeholder_text="100",
            border_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO,
            width=70
        )
        self.entry_limite.insert(0, "100")
        self.entry_limite.grid(row=0, column=col, padx=(0, 5), pady=pad_y, sticky="w")
        col += 1

        self.switch_modo = ctk.CTkSwitch(
            linha,
            text="S/ m\u00e1q.",
            font=("Segoe UI", 12),
            progress_color=COR_PRIMARIA,
            button_color=COR_PRIMARIA,
            button_hover_color=COR_TEXTO_SECUNDARIO,
            onvalue=True,
            offvalue=False,
            switch_width=36
        )
        self.switch_modo.select()
        self.switch_modo.grid(row=0, column=col, padx=(0, 10), pady=pad_y, sticky="w")
        col += 1

        self.botao_aplicar = ctk.CTkButton(
            linha,
            text="\U0001F50D  APLICAR",
            font=("Segoe UI", 12, "bold"),
            command=self.aplicar_filtros,
            fg_color=COR_SUCESSO,
            hover_color=COR_SUCESSO_HOVER,
            text_color=COR_TEXTO_BRANCO,
            height=33,
            corner_radius=8
        )
        self.botao_aplicar.grid(row=0, column=col, padx=(0, 12), pady=pad_y, sticky="e")

    def _criar_barra_exclusao(self):
        frame_exc = ctk.CTkFrame(self, fg_color="transparent")
        frame_exc.grid(row=2, column=0, sticky="ew", padx=40, pady=(5, 5))
        frame_exc.grid_columnconfigure(0, weight=1)

        card = ctk.CTkFrame(frame_exc, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        card.grid(row=0, column=0, sticky="ew")
        card.grid_columnconfigure(2, weight=1)

        label_exc = ctk.CTkLabel(
            card, text="Excluir descri\u00e7\u00e3o:",
            font=("Segoe UI", 12, "bold"), text_color=COR_ERRO
        )
        label_exc.grid(row=0, column=0, padx=(15, 8), pady=10, sticky="w")

        self.botao_excluir_descricao = ctk.CTkButton(
            card,
            text="\u25BC Descri\u00e7\u00e3o",
            font=("Segoe UI", 11),
            command=self._abrir_exclusao_descricao,
            fg_color="transparent",
            text_color=COR_TEXTO,
            hover_color=COR_BORDA,
            border_color=COR_TEXTO_SECUNDARIO,
            border_width=1,
            height=28,
            corner_radius=6
        )
        self.botao_excluir_descricao.grid(row=0, column=1, padx=3, pady=10, sticky="w")

        self.label_exclusao_status = ctk.CTkLabel(
            card, text="",
            font=("Segoe UI", 11), text_color=COR_AVISO, anchor="w"
        )
        self.label_exclusao_status.grid(row=0, column=2, padx=(10, 15), pady=10, sticky="w")
        self._atualizar_status_exclusao()

        self.botao_limpar_exclusao = ctk.CTkButton(
            card,
            text="\u2716 Limpar Exclus\u00e3o",
            font=("Segoe UI", 11),
            command=self._limpar_exclusao_descricao,
            fg_color=COR_TEXTO_BRANCO,
            text_color=COR_ERRO,
            hover_color=COR_BORDA,
            border_color=COR_ERRO,
            border_width=1,
            height=28,
            corner_radius=6
        )
        self.botao_limpar_exclusao.grid(row=0, column=3, padx=(0, 15), pady=10, sticky="e")

    def _abrir_exclusao_descricao(self):
        base = self.controller.sugestao_base
        if base is None or base.empty:
            messagebox.showinfo("Aviso", "Aplique os crit\u00e9rios primeiro para carregar os dados.")
            return

        valores_unicos = base["descricao_material"].dropna().unique().tolist()
        if not valores_unicos:
            messagebox.showinfo("Aviso", "Nenhuma descri\u00e7\u00e3o dispon\u00edvel.")
            return

        popup = FiltroColunaPopup(
            self,
            nome_coluna="Descri\u00e7\u00e3o",
            valores_unicos=valores_unicos,
            excluidos=self.controller.descricao_excluir
        )
        self.wait_window(popup)

        if popup.resultado is not None:
            manter = popup.resultado
            if len(manter) < len(valores_unicos):
                self.controller.descricao_excluir = set(valores_unicos) - manter
            else:
                self.controller.descricao_excluir = set()
            self._atualizar_status_exclusao()
            self.aplicar_filtros()

    def _limpar_exclusao_descricao(self):
        self.controller.descricao_excluir = set()
        self._atualizar_status_exclusao()
        self.aplicar_filtros()

    def _atualizar_status_exclusao(self):
        qtd = len(self.controller.descricao_excluir)
        if qtd > 0:
            self.botao_excluir_descricao.configure(
                fg_color=COR_ERRO, text_color=COR_TEXTO_BRANCO, border_color=COR_ERRO
            )
            self.label_exclusao_status.configure(
                text=f"{qtd} descri\u00e7\u00e3o(\u00f5es) exclu\u00edda(s)",
                text_color=COR_AVISO
            )
        else:
            self.botao_excluir_descricao.configure(
                fg_color="transparent", text_color=COR_TEXTO, border_color=COR_TEXTO_SECUNDARIO
            )
            self.label_exclusao_status.configure(text="Nenhuma exclus\u00e3o ativa", text_color=COR_TEXTO_SECUNDARIO)

    def _criar_tabela(self):
        self.tabela = TabelaDados(self, COLUNAS_TABELA)
        self.tabela.grid(row=3, column=0, sticky="nsew", padx=40, pady=(5, 5))

    def _criar_barra_acoes(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=4, column=0, sticky="ew", padx=40, pady=(5, 10))
        frame.grid_columnconfigure(0, weight=1)

        barra = ctk.CTkFrame(frame, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=8)
        barra.grid(row=0, column=0, sticky="ew")
        barra.grid_columnconfigure(4, weight=1)

        self.label_totais = ctk.CTkLabel(
            barra,
            text="Lotes: 0  |  Posi\u00e7\u00f5es: 0  |  Valor Total: R$ 0,00",
            font=("Segoe UI", 13, "bold"),
            text_color=COR_TEXTO
        )
        self.label_totais.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        self.botao_gerar = ctk.CTkButton(
            barra,
            text="\u25B6  GERAR DOCUMENTO",
            font=("Segoe UI", 14, "bold"),
            command=self.gerar_documento,
            fg_color=COR_SUCESSO,
            hover_color=COR_SUCESSO_HOVER,
            text_color=COR_TEXTO_BRANCO,
            state="disabled",
            height=45,
            width=220,
            corner_radius=8
        )
        self.botao_gerar.grid(row=0, column=1, padx=(0, 10), pady=13, sticky="e")

        self.botao_ver_documento = ctk.CTkButton(
            barra,
            text="\U0001F4C4  Ver \u00daltimo Documento",
            font=("Segoe UI", 13),
            command=self._ver_ultimo_documento,
            fg_color=COR_PRIMARIA,
            hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO,
            state="disabled",
            height=38,
            width=210,
            corner_radius=8
        )
        self.botao_ver_documento.grid(row=0, column=2, padx=(0, 10), pady=13, sticky="e")

        self.botao_importar = ctk.CTkButton(
            barra,
            text="\U0001F4E5  Atualizar Dados",
            font=("Segoe UI", 13),
            command=self.importar_dados,
            fg_color=COR_PRIMARIA,
            hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO,
            state="disabled",
            height=38,
            width=170,
            corner_radius=8
        )
        self.botao_importar.grid(row=0, column=3, padx=(0, 15), pady=13, sticky="e")

    # --- Filtros / Consulta ---

    def aplicar_filtros(self):
        if self.controller.estoque is None:
            messagebox.showwarning("Aguarde", "Os dados ainda est\u00e3o sendo carregados.")
            return

        criterio = CRITERIOS_UI[self.combo_criterio.get()]
        criterio_sec = CRITERIO_SECUNDARIO_MAP[self.combo_criterio2.get()]
        tipo = self.combo_tipo.get()
        try:
            limite = int(self.entry_limite.get())
        except ValueError:
            limite = 100
        modo_sem_maquina = self.switch_modo.get()
        self.ultimo_modo_sem_maquina = modo_sem_maquina

        self.botao_aplicar.configure(state="disabled", text="CARREGANDO...")

        threading.Thread(
            target=self._executar_consulta,
            args=(criterio, criterio_sec, tipo, limite, modo_sem_maquina),
            daemon=True
        ).start()

    def _executar_consulta(self, criterio, criterio_sec, tipo, limite, modo_sem_maquina):
        try:
            resultado = self.controller.consultar_estoque(
                criterio=criterio,
                tipo_deposito=tipo,
                limite_posicoes=limite,
                modo_sem_maquina=modo_sem_maquina,
                criterio_secundario=criterio_sec
            )
            self.after(0, lambda: self._pos_consulta(resultado, modo_sem_maquina))
        except Exception as e:
            self.after(0, lambda: self._erro_consulta(str(e)))

    def _pos_consulta(self, resultado, modo_sem_maquina=False):
        if resultado.empty:
            mensagem = None
            if modo_sem_maquina:
                mensagem = (
                    "N\u00e3o existem lotes com 100% das posi\u00e7\u00f5es "
                    "no n\u00edvel 1 ou abaixo no momento."
                )
            elif self.controller.descricao_excluir:
                mensagem = "Todas as descri\u00e7\u00f5es foram exclu\u00eddas. Use \"\u2716 Limpar Exclus\u00e3o\" para redefinir."
            else:
                mensagem = "Nenhum lote encontrado para os crit\u00e9rios selecionados."

            self.tabela.mostrar_mensagem(mensagem)
            self.label_totais.configure(
                text="Lotes: 0  |  Posi\u00e7\u00f5es: 0  |  Valor Total: R$ 0,00"
            )
        else:
            self.tabela.carregar(resultado)

        total_lotes = len(resultado)
        total_posicoes = int(resultado["quantidade_posicoes"].sum()) if not resultado.empty else 0
        total_valor = resultado["valor_lote"].sum() if not resultado.empty else 0
        valor_str = f"R$ {total_valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        self.label_totais.configure(
            text=f"Lotes: {total_lotes}  |  Posi\u00e7\u00f5es: {total_posicoes}  |  Valor Total: {valor_str}"
        )

        self.botao_aplicar.configure(state="normal", text="\U0001F50D  APLICAR")

    def _erro_consulta(self, erro):
        self.botao_aplicar.configure(state="normal", text="\U0001F50D  APLICAR")
        messagebox.showerror("Erro", f"Erro ao consultar estoque:\n{erro}")

    # --- Geração do Documento ---

    def gerar_documento(self):
        if self.controller.estoque is None:
            messagebox.showwarning("Aguarde", "Os dados ainda est\u00e3o sendo carregados.")
            return

        criterio = CRITERIOS_UI[self.combo_criterio.get()]
        criterio_sec = CRITERIO_SECUNDARIO_MAP[self.combo_criterio2.get()]
        tipo = self.combo_tipo.get()
        try:
            limite = int(self.entry_limite.get())
        except ValueError:
            limite = 100
        modo_sem_maquina = self.switch_modo.get()

        self.botao_gerar.configure(state="disabled", text="GERANDO...")
        self.rodape.atualizar("Gerando documento...")
        self.rodape.mostrar_progresso()

        threading.Thread(
            target=self._executar_geracao,
            args=(criterio, criterio_sec, tipo, limite, modo_sem_maquina),
            daemon=True
        ).start()

    def _executar_geracao(self, criterio, criterio_sec, tipo, limite, modo_sem_maquina):
        try:
            resultado = self.controller.gerar(
                criterio=criterio,
                tipo_deposito=tipo,
                limite_posicoes=limite,
                modo_sem_maquina=modo_sem_maquina,
                criterio_secundario=criterio_sec
            )
            self.after(0, lambda: self._pos_geracao(resultado))
        except Exception as e:
            self.after(0, lambda: self._erro_geracao(str(e)))

    def _pos_geracao(self, resultado):
        self.rodape.esconder_progresso()
        self.botao_gerar.configure(state="normal", text="\u25B6  GERAR DOCUMENTO")
        self.rodape.atualizar("Documento gerado com sucesso")

        self.botao_ver_documento.configure(state="normal")

        if self.ao_exibir_resultado:
            self.ao_exibir_resultado(resultado)

    def _atualizar_botao_ver_documento(self):
        if self.controller.ultimo_resultado is not None:
            self.botao_ver_documento.configure(state="normal")
        else:
            self.botao_ver_documento.configure(state="disabled")

    def _ver_ultimo_documento(self):
        if self.controller.ultimo_resultado:
            self.ao_exibir_resultado(self.controller.ultimo_resultado)

    def _erro_geracao(self, erro):
        self.rodape.esconder_progresso()
        self.botao_gerar.configure(state="normal", text="\u25B6  GERAR DOCUMENTO")
        self.rodape.atualizar(f"Erro: {erro}")
        messagebox.showerror("Erro", f"Erro ao gerar documento:\n{erro}")

    # --- Importação de Dados ---

    def importar_dados(self):
        messagebox.showinfo(
            "Atualizar Dados",
            "Selecione o arquivo LX02 do dia."
        )
        lx02 = filedialog.askopenfilename(
            title="Selecione o arquivo LX02",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")]
        )
        if not lx02:
            return

        messagebox.showinfo(
            "Atualizar Dados",
            "Agora selecione o arquivo YMM141 do dia."
        )
        ymm141 = filedialog.askopenfilename(
            title="Selecione o arquivo YMM141",
            filetypes=[("Excel", "*.xlsx"), ("Todos", "*.*")]
        )
        if not ymm141:
            return

        self.rodape.atualizar("Importando dados...")
        self.rodape.mostrar_progresso()
        self.botao_importar.configure(state="disabled")

        threading.Thread(target=self._executar_importacao, args=(
            lx02, ymm141
        ), daemon=True).start()

    def _executar_importacao(self, lx02, ymm141):
        try:
            shutil.copy2(lx02, os.path.join(ENTRADA_DIR, "LX02.xlsx"))
            shutil.copy2(ymm141, os.path.join(ENTRADA_DIR, "YMM141.xlsx"))

            tipos = self.controller.carregar()
            self.after(0, lambda: self._pos_importacao(tipos))
        except Exception as e:
            self.after(0, lambda: self._erro(str(e)))

    def _pos_importacao(self, tipos):
        self.rodape.esconder_progresso()
        self.botao_importar.configure(state="normal")
        self.tabela.limpar()
        self.combo_tipo.configure(values=tipos)
        if tipos:
            self.combo_tipo.set(tipos[0])
        self._atualizar_status_exclusao()
        self._atualizar_botao_ver_documento()
        self.label_totais.configure(
            text="Lotes: 0  |  Posi\u00e7\u00f5es: 0  |  Valor Total: R$ 0,00"
        )
        self.rodape.atualizar("Dados importados com sucesso")
