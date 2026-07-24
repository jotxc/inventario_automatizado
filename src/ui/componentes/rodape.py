from ui.tema import COR_TEXTO_SECUNDARIO, COR_AVISO, VERSAO
import customtkinter as ctk


class Rodape(ctk.CTkFrame):

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        self.label_status = ctk.CTkLabel(
            self,
            text="Status: Inicializando...",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="w"
        )
        self.label_status.grid(row=0, column=0, padx=(20, 5), pady=10, sticky="w")

        self.label_exclusao = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 11, "bold"),
            text_color=COR_AVISO,
            anchor="w"
        )
        self.label_exclusao.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        self.label_versao = ctk.CTkLabel(
            self,
            text=f"v{VERSAO}",
            font=("Segoe UI", 11),
            text_color=COR_TEXTO_SECUNDARIO,
            anchor="e"
        )
        self.label_versao.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        self.progress_bar = ctk.CTkProgressBar(
            self,
            mode="indeterminate",
            height=3
        )

    def atualizar(self, texto):
        self.label_status.configure(text=f"Status: {texto}")

    def atualizar_exclusao(self, quantos):
        if quantos > 0:
            self.label_exclusao.configure(
                text=f"\u26A0  {quantos} material(is) exclu\u00eddo(s) do documento"
            )
        else:
            self.label_exclusao.configure(text="")

    def mostrar_progresso(self):
        self.progress_bar.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.progress_bar.start()

    def esconder_progresso(self):
        self.progress_bar.grid_forget()
        self.progress_bar.stop()
