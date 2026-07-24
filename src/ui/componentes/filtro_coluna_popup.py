import customtkinter as ctk
from ui.tema import (
    COR_PRIMARIA, COR_TEXTO, COR_TEXTO_BRANCO, COR_TEXTO_SECUNDARIO,
    COR_FUNDO, COR_CARD, COR_BORDA
)


class FiltroColunaPopup(ctk.CTkToplevel):

    def __init__(self, master, nome_coluna, valores_unicos, excluidos=None):
        super().__init__(master)
        self.valores_unicos = sorted(valores_unicos, key=str)
        self.valores_filtrados = []
        excluidos = excluidos or set()
        self.estado_valores = {v: v not in excluidos for v in self.valores_unicos}
        self.resultado = None
        self._debounce_id = None

        self.title(f"Excluir - {nome_coluna}")
        self.geometry("450x500")
        self.resizable(True, True)
        self.transient(master)
        self.grab_set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        frame_top = ctk.CTkFrame(self, fg_color="transparent")
        frame_top.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        frame_top.grid_columnconfigure(1, weight=1)

        label_titulo = ctk.CTkLabel(
            frame_top, text=f"Excluir materiais - {nome_coluna}",
            font=("Segoe UI", 14, "bold"), text_color=COR_PRIMARIA
        )
        label_titulo.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        self.entry_busca = ctk.CTkEntry(
            frame_top, placeholder_text="Digite para filtrar...",
            border_color=COR_TEXTO_SECUNDARIO, text_color=COR_TEXTO
        )
        self.entry_busca.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        self.entry_busca.bind("<KeyRelease>", self._iniciar_debounce)

        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=1, column=0, sticky="ew", padx=15, pady=(10, 5))

        self.botao_selecionar_todos = ctk.CTkButton(
            frame_botoes, text="Selecionar Todos",
            font=("Segoe UI", 11), command=self._selecionar_todos,
            fg_color=COR_TEXTO_BRANCO, text_color=COR_TEXTO,
            hover_color=COR_BORDA, border_color=COR_TEXTO_SECUNDARIO,
            border_width=1, height=28, width=130, corner_radius=6
        )
        self.botao_selecionar_todos.grid(row=0, column=0, padx=(0, 5), pady=0)

        self.botao_limpar_todos = ctk.CTkButton(
            frame_botoes, text="Limpar Todos",
            font=("Segoe UI", 11), command=self._limpar_todos,
            fg_color=COR_TEXTO_BRANCO, text_color=COR_TEXTO,
            hover_color=COR_BORDA, border_color=COR_TEXTO_SECUNDARIO,
            border_width=1, height=28, width=130, corner_radius=6
        )
        self.botao_limpar_todos.grid(row=0, column=1, padx=(5, 0), pady=0)

        self.frame_lista = ctk.CTkScrollableFrame(
            self, fg_color=COR_CARD, border_color=COR_BORDA, border_width=1, corner_radius=6
        )
        self.frame_lista.grid(row=2, column=0, sticky="nsew", padx=15, pady=5)
        self.frame_lista.grid_columnconfigure(0, weight=1)

        self.label_placeholder = ctk.CTkLabel(
            self.frame_lista, text="Digite acima para buscar descri\u00e7\u00f5es...",
            font=("Segoe UI", 13), text_color=COR_TEXTO_SECUNDARIO
        )
        self.label_placeholder.grid(row=0, column=0, padx=10, pady=20)

        self.checkboxes = []

        frame_rodape = ctk.CTkFrame(self, fg_color="transparent")
        frame_rodape.grid(row=3, column=0, sticky="ew", padx=15, pady=(5, 15))

        for i in range(2):
            frame_rodape.grid_columnconfigure(i, weight=1)

        self.botao_aplicar = ctk.CTkButton(
            frame_rodape, text="Aplicar",
            font=("Segoe UI", 13, "bold"), command=self._aplicar,
            fg_color=COR_PRIMARIA, hover_color=COR_TEXTO_SECUNDARIO,
            text_color=COR_TEXTO_BRANCO, height=35, corner_radius=8
        )
        self.botao_aplicar.grid(row=0, column=0, padx=(0, 5), pady=0, sticky="ew")

        self.botao_cancelar = ctk.CTkButton(
            frame_rodape, text="Cancelar",
            font=("Segoe UI", 13, "bold"), command=self._cancelar,
            fg_color=COR_TEXTO_BRANCO, text_color=COR_TEXTO,
            hover_color=COR_BORDA, border_color=COR_TEXTO_SECUNDARIO,
            border_width=1, height=35, corner_radius=8
        )
        self.botao_cancelar.grid(row=0, column=1, padx=(5, 0), pady=0, sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self._cancelar)

    def _iniciar_debounce(self, event=None):
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(200, self._filtrar_valores)

    def _recriar_checkboxes(self, parent):
        for cb in self.checkboxes:
            cb[0].destroy()
        self.checkboxes.clear()

        if not self.valores_filtrados:
            self.label_placeholder.grid()
            return

        self.label_placeholder.grid_remove()

        for valor in self.valores_filtrados:
            var = ctk.BooleanVar(value=self.estado_valores.get(valor, True))
            cb = ctk.CTkCheckBox(
                parent, text=str(valor), variable=var,
                font=("Segoe UI", 12), text_color=COR_TEXTO,
                fg_color=COR_PRIMARIA, hover_color=COR_TEXTO_SECUNDARIO,
                border_color=COR_TEXTO_SECUNDARIO, corner_radius=4,
                checkbox_width=20, checkbox_height=20
            )
            cb.grid(row=len(self.checkboxes), column=0, sticky="w", padx=10, pady=2)
            self.checkboxes.append((cb, var, valor))

    def _filtrar_valores(self, event=None):
        self._salvar_estado_visivel()
        termo = self.entry_busca.get().strip().lower()
        if termo:
            self.valores_filtrados = [v for v in self.valores_unicos if termo in str(v).lower()]
        else:
            self.valores_filtrados = []

        self._recriar_checkboxes(self.frame_lista)

    def _salvar_estado_visivel(self):
        for _, var, valor in self.checkboxes:
            self.estado_valores[valor] = var.get()

    def _selecionar_todos(self):
        for _, var, _ in self.checkboxes:
            var.set(True)
        for v in self.estado_valores:
            self.estado_valores[v] = True

    def _limpar_todos(self):
        for _, var, _ in self.checkboxes:
            var.set(False)
        for v in self.valores_filtrados:
            self.estado_valores[v] = False

    def _obter_manter(self):
        self._salvar_estado_visivel()
        return {v for v, checked in self.estado_valores.items() if checked}

    def _aplicar(self):
        self.resultado = self._obter_manter()
        self.destroy()

    def _cancelar(self):
        self.resultado = None
        self.destroy()