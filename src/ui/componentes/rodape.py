from ui.tema import COR_TEXTO_SECUNDARIO, VERSAO
import customtkinter as ctk


class Rodape(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(0, weight=1)

        self.label_status = ctk.CTkLabel(
            self,
            text="Status: Inicializando...",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        )
        self.label_status.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        self.label_versao = ctk.CTkLabel(
            self,
            text=f"v{VERSAO}",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="e"
        )
        self.label_versao.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            height=3
        )

    def atualizar(self, texto):
        self.label_status.configure(text=f"Status: {texto}")

    def mostrar_progresso(self):
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.progress_bar.start()

    def esconder_progresso(self):
        self.progress_bar.grid_forget()
        self.progress_bar.stop()
