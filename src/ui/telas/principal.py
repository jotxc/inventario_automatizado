import threading
import os
import shutil
import platform
import subprocess
import customtkinter as ctk
from tkinter import messagebox, filedialog

from config.config import ARQUIVO_SAIDA, ARQUIVO_HISTORICO, ENTRADA_DIR, CRITERIOS_UI
from controller.inventario_controller import InventarioController
from ui.tema import COR_FUNDO
from ui.componentes.cabecalho import Cabecalho
from ui.componentes.formulario import Formulario
from ui.componentes.resumo import Resumo
from ui.componentes.barra_acoes import BarraAcoes
from ui.componentes.rodape import Rodape


class TelaPrincipal(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color=COR_FUNDO)
        self.controller = InventarioController()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.cabecalho = Cabecalho(self)
        self.cabecalho.grid(row=0, column=0, sticky="ew")

        frame_meio = ctk.CTkFrame(self, fg_color="transparent")
        frame_meio.grid(row=1, column=0, sticky="nsew", padx=40, pady=20)
        frame_meio.grid_columnconfigure(0, weight=3)
        frame_meio.grid_columnconfigure(1, weight=2)
        frame_meio.grid_rowconfigure(0, weight=1)

        self.formulario = Formulario(frame_meio, ao_gerar=self.gerar_documento)
        self.formulario.grid(row=0, column=0, sticky="new", padx=(0, 10))

        self.resumo = Resumo(frame_meio)
        self.resumo.grid(row=0, column=1, sticky="new", padx=(10, 0))

        self.barra_acoes = BarraAcoes(self, ao_importar=self.importar_dados)
        self.barra_acoes.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 10))
        self.barra_acoes.botao_documento.configure(command=self.abrir_documento)
        self.barra_acoes.botao_historico.configure(command=self.abrir_historico)

        self.rodape = Rodape(self)
        self.rodape.grid(row=3, column=0, sticky="ew", padx=40, pady=(0, 15))

        self.update_idletasks()
        self.after(300, self.iniciar_carregamento)

    def iniciar_carregamento(self):
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
        self.formulario.combo_tipo.configure(values=tipos)
        if tipos:
            self.formulario.combo_tipo.set(tipos[0])
        self.rodape.atualizar("Pronto")

    def gerar_documento(self):
        if self.controller.estoque is None:
            messagebox.showwarning("Aguarde", "Os dados ainda estão sendo carregados.")
            return

        criterio_label = self.formulario.combo_criterio.get()
        criterio = CRITERIOS_UI[criterio_label]
        tipo = self.formulario.combo_tipo.get()
        limite = int(self.formulario.entry_limite.get())
        modo_sem_maquina = self.formulario.switch_modo.get()

        self.formulario.botao_gerar.configure(state="disabled", text="GERANDO...")
        self.rodape.atualizar("Gerando documento...")
        self.rodape.mostrar_progresso()

        threading.Thread(target=self._executar_geracao, args=(
            criterio_label, criterio, tipo, limite, modo_sem_maquina
        ), daemon=True).start()

    def _executar_geracao(self, criterio_label, criterio, tipo, limite, modo_sem_maquina):
        try:
            resultado = self.controller.gerar(
                criterio=criterio,
                limite_posicoes=limite,
                tipo_deposito=tipo,
                modo_sem_maquina=modo_sem_maquina
            )
            self.after(0, lambda: self._pos_geracao(criterio_label, resultado))
        except Exception as e:
            self.after(0, lambda: self._erro_geracao(str(e)))

    def _pos_geracao(self, criterio_label, resultado):
        self.rodape.esconder_progresso()
        sugestao = resultado["sugestao"]
        dados = {
            "criterio": criterio_label,
            "tipo_deposito": resultado["tipo_deposito"],
            "lotes": len(sugestao),
            "posicoes": int(sugestao["quantidade_posicoes"].sum()),
            "valor": sugestao["valor_lote"].sum(),
            "arquivo": resultado["arquivo"]
        }
        self.resumo.atualizar(dados)
        self.barra_acoes.botao_documento.configure(state="normal")
        self.formulario.botao_gerar.configure(state="normal", text="\u25B6  GERAR DOCUMENTO")
        self.rodape.atualizar("Documento gerado com sucesso")

    def _erro_geracao(self, erro):
        self.rodape.esconder_progresso()
        self.formulario.botao_gerar.configure(state="normal", text="\u25B6  GERAR DOCUMENTO")
        self.rodape.atualizar(f"Erro: {erro}")
        messagebox.showerror("Erro", f"Erro ao gerar documento:\n{erro}")

    def _erro(self, erro):
        self.rodape.esconder_progresso()
        self.rodape.atualizar(f"Erro: {erro}")

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
        self.barra_acoes.botao_importar.configure(state="disabled")

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
        self.barra_acoes.botao_importar.configure(state="normal")
        self.barra_acoes.botao_documento.configure(state="disabled")
        self.resumo.limpar()
        self.formulario.combo_tipo.configure(values=tipos)
        if tipos:
            self.formulario.combo_tipo.set(tipos[0])
        self.rodape.atualizar("Dados importados com sucesso")

    def abrir_documento(self):
        if not os.path.exists(ARQUIVO_SAIDA):
            messagebox.showwarning("Arquivo", "Nenhum documento foi gerado ainda.")
            return
        self._abrir_arquivo(ARQUIVO_SAIDA)

    def abrir_historico(self):
        if not os.path.exists(ARQUIVO_HISTORICO):
            messagebox.showwarning("Histórico", "Histórico não encontrado.")
            return
        self._abrir_arquivo(ARQUIVO_HISTORICO)

    @staticmethod
    def _abrir_arquivo(caminho):
        if platform.system() == "Windows":
            os.startfile(caminho)
        else:
            subprocess.call(["open", caminho])
