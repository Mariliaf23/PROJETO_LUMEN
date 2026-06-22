import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from tkinter import filedialog
from dotenv import load_dotenv
from services.styles import (
    COR_BG, COR_DOURADO, COR_TEXTO, COR_TEXTO2, COR_CARD, COR_INPUT_BORDER,
    FONTE_TITULO, FONTE_SUBTITULO, FONTE_LABEL,
    criar_entry, criar_botao_preenchido, criar_botao, criar_label, criar_titulo,
    criar_card
)


class TelaConfiguracoes(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=COR_BG)
        self.controller = controller

        self._env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        self._carregar_valores()
        self._construir_ui()

    def _carregar_valores(self):
        load_dotenv(self._env_path, override=True)
        self.valores = {
            'DB_HOST': os.getenv('DB_HOST', 'localhost'),
            'DB_USER': os.getenv('DB_USER', 'root'),
            'DB_PASSWORD': os.getenv('DB_PASSWORD', ''),
            'DB_NAME': os.getenv('DB_NAME', 'biblioteca'),
            'DEFAULT_USER': os.getenv('DEFAULT_USER', 'admin'),
            'DEFAULT_PASSWORD': os.getenv('DEFAULT_PASSWORD', 'admin123'),
        }

    def _ao_visitar(self):
        self._carregar_valores()
        self._reconstruir()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=30)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 25))

        criar_titulo(header, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left")
        criar_label(header, "Configuracoes", font=FONTE_SUBTITULO, text_color=COR_TEXTO).pack(side="left", padx=(15, 0))

        btn_voltar = criar_botao(header, text="Voltar", command=self._voltar, width=100, height=35)
        btn_voltar.pack(side="right")

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        db_card = criar_card(scroll)
        db_card.pack(fill="x", pady=(0, 20))

        criar_titulo(db_card, "Banco de Dados", font=("Cinzel", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        db_frame = ctk.CTkFrame(db_card, fg_color="transparent")
        db_frame.pack(fill="x", padx=20, pady=(0, 15))
        db_frame.grid_columnconfigure((0, 1), weight=1)

        criar_label(db_frame, "Host", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.entry_db_host = criar_entry(db_frame, height=38)
        self.entry_db_host.insert(0, self.valores['DB_HOST'])
        self.entry_db_host.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        criar_label(db_frame, "Usuario", font=FONTE_LABEL).grid(row=0, column=1, sticky="w", pady=(0, 3))
        self.entry_db_user = criar_entry(db_frame, height=38)
        self.entry_db_user.insert(0, self.valores['DB_USER'])
        self.entry_db_user.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        criar_label(db_frame, "Senha", font=FONTE_LABEL).grid(row=2, column=0, sticky="w", pady=(10, 3))
        self.entry_db_password = criar_entry(db_frame, height=38, show="*")
        self.entry_db_password.insert(0, self.valores['DB_PASSWORD'])
        self.entry_db_password.grid(row=3, column=0, padx=(0, 10), sticky="ew")

        criar_label(db_frame, "Banco", font=FONTE_LABEL).grid(row=2, column=1, sticky="w", pady=(10, 3))
        self.entry_db_name = criar_entry(db_frame, height=38)
        self.entry_db_name.insert(0, self.valores['DB_NAME'])
        self.entry_db_name.grid(row=3, column=1, padx=(10, 0), sticky="ew")

        user_card = criar_card(scroll)
        user_card.pack(fill="x", pady=(0, 20))

        criar_titulo(user_card, "Usuario Padrao", font=("Cinzel", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        user_frame = ctk.CTkFrame(user_card, fg_color="transparent")
        user_frame.pack(fill="x", padx=20, pady=(0, 15))
        user_frame.grid_columnconfigure((0, 1), weight=1)

        criar_label(user_frame, "Usuario", font=FONTE_LABEL).grid(row=0, column=0, sticky="w", pady=(0, 3))
        self.entry_default_user = criar_entry(user_frame, height=38)
        self.entry_default_user.insert(0, self.valores['DEFAULT_USER'])
        self.entry_default_user.grid(row=1, column=0, padx=(0, 10), sticky="ew")

        criar_label(user_frame, "Senha", font=FONTE_LABEL).grid(row=0, column=1, sticky="w", pady=(0, 3))
        self.entry_default_password = criar_entry(user_frame, height=38, show="*")
        self.entry_default_password.insert(0, self.valores['DEFAULT_PASSWORD'])
        self.entry_default_password.grid(row=1, column=1, padx=(10, 0), sticky="ew")

        self.btn_salvar = criar_botao_preenchido(
            scroll, text="Salvar Configuracoes", command=self._salvar,
            width=280, height=44
        )
        self.btn_salvar.pack(pady=(10, 20))

        report_card = criar_card(scroll)
        report_card.pack(fill="x", pady=(0, 20))

        criar_titulo(report_card, "Relatorios", font=("Cinzel", 16, "bold")).pack(anchor="w", padx=20, pady=(15, 10))

        report_frame = ctk.CTkFrame(report_card, fg_color="transparent")
        report_frame.pack(fill="x", padx=20, pady=(0, 15))

        criar_botao_preenchido(
            report_frame, text="Relatorio de Livros", command=lambda: self._gerar_relatorio('livros'),
            width=200, height=38
        ).pack(side="left", padx=(0, 10))

        criar_botao_preenchido(
            report_frame, text="Relatorio de Emprestimos", command=lambda: self._gerar_relatorio('emprestimos'),
            width=220, height=38
        ).pack(side="left", padx=(0, 10))

        criar_botao_preenchido(
            report_frame, text="Relatorio de Multas", command=lambda: self._gerar_relatorio('multas'),
            width=200, height=38
        ).pack(side="left")

        self.lbl_notificacao = criar_label(scroll, "", text_color=COR_TEXTO2)

    def _reconstruir(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._construir_ui()

    def _salvar(self):
        novos_valores = {
            'DB_HOST': self.entry_db_host.get().strip(),
            'DB_USER': self.entry_db_user.get().strip(),
            'DB_PASSWORD': self.entry_db_password.get().strip(),
            'DB_NAME': self.entry_db_name.get().strip(),
            'DEFAULT_USER': self.entry_default_user.get().strip(),
            'DEFAULT_PASSWORD': self.entry_default_password.get().strip(),
        }

        linhas = [f"{k}={v}" for k, v in novos_valores.items()]
        with open(self._env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas) + '\n')

        self._notificar("Configuracoes salvas! Reinicie o sistema.")

    def _voltar(self):
        self.controller.voltar()

    def _gerar_relatorio(self, tipo):
        from services.report_gen import (
            gerar_relatorio_livros, gerar_relatorio_emprestimos, gerar_relatorio_multas
        )
        caminho = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title=f"Salvar Relatorio de {tipo.title()}"
        )
        if not caminho:
            return
        try:
            if tipo == 'livros':
                gerar_relatorio_livros(caminho)
            elif tipo == 'emprestimos':
                gerar_relatorio_emprestimos(caminho)
            elif tipo == 'multas':
                gerar_relatorio_multas(caminho)
            self._notificar(f"Relatorio salvo em: {caminho}")
        except Exception as e:
            self._notificar(f"Erro ao gerar relatorio: {e}")

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color="#d4b896")
        self.lbl_notificacao.pack(pady=(10, 0))
        self.after(3000, lambda: self.lbl_notificacao.configure(text=""))
