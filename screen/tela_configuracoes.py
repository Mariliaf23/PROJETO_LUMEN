import os
import sys
import shutil
from PIL import Image
from dotenv import load_dotenv
from tkinter import filedialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.styles import (
    cores,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo
)
from services.database_config import listar_turmas, cadastrar_turma, excluir_turma


class TelaConfiguracoes(ctk.CTkFrame):
    def __init__(self, master=None, controller=None):
        self.cor_bg = str(cores.COR_BG)
        self.cor_card = str(cores.COR_CARD)
        self.cor_texto = str(cores.COR_TEXTO)
        self.cor_texto2 = str(cores.COR_TEXTO2)

        super().__init__(master, fg_color=self.cor_bg)
        self.controller = controller

        self._caminho_base = os.path.dirname(os.path.dirname(__file__))
        self._assets_dir = os.path.join(self._caminho_base, "assets")
        self._logo_escola_path = os.path.join(self._assets_dir, "logo_escola.png")
        self._env_path = os.path.join(self._caminho_base, '.env')
        self._logo_ctk = None
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
            'SCHOOL_NAME': os.getenv('SCHOOL_NAME', ''),
        }

    def _ao_visitar(self):
        self._carregar_valores()
        self._reconstruir()

    def _construir_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=30, pady=15)

        # HEADER compactado
        header = ctk.CTkFrame(container, fg_color=cores.COR_CARD)
        header.pack(fill="x", pady=(0, 10))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        logo_lumen = os.path.join(self._assets_dir, "logo_lumen.png")
        if os.path.exists(logo_lumen):
            try:
                img = ctk.CTkImage(Image.open(logo_lumen), size=(55, 55))
                ctk.CTkLabel(header_left, image=img, text="").pack(side="left", padx=(0, 15))
            except:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        criar_label(header_left, "Configurações do Sistema", font=("Segoe UI", 24, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        # Botões: Salvar + Voltar (lado a lado)
        header_right = ctk.CTkFrame(header, fg_color="transparent")
        header_right.pack(side="right", padx=15, pady=5)

        self.btn_salvar = ctk.CTkButton(
            header_right, text="Salvar", command=self._salvar,
            width=100, height=36, fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 14, "bold")
        )
        self.btn_salvar.pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            header_right, text="Voltar", command=self._voltar,
            width=100, height=36, fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF",
            border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 14, "bold")
        ).pack(side="left", padx=(0, 10))

        self.lbl_notificacao = ctk.CTkLabel(header_right, text="", font=("Segoe UI", 12, "bold"), text_color=cores.COR_AZUL_HOVER)
        self.lbl_notificacao.pack(side="left")

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # === CARD: ESCOLA (NOME + LOGO) ===
        escola_card = criar_card(scroll)
        escola_card.pack(fill="x", pady=(0, 15))

        criar_label(escola_card, "ESCOLA", font=("Segoe UI", 20, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        escola_frame = ctk.CTkFrame(escola_card, fg_color="transparent")
        escola_frame.pack(fill="x", padx=20, pady=(0, 15))
        escola_frame.grid_columnconfigure(1, weight=1)

        # Nome da escola
        criar_label(escola_frame, "Nome da Escola", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 3))
        self.entry_school_name = criar_entry(escola_frame, height=38)
        self.entry_school_name.insert(0, self.valores['SCHOOL_NAME'])
        self.entry_school_name.grid(row=1, column=0, columnspan=2, padx=20, sticky="ew")

        # Logo da escola
        logo_frame = ctk.CTkFrame(escola_frame, fg_color="transparent")
        logo_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(15, 0), sticky="ew")

        criar_label(logo_frame, "Logo da Escola", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", pady=(0, 8))

        logo_area = ctk.CTkFrame(logo_frame, fg_color="transparent")
        logo_area.pack(fill="x")

        # Área de visualização da logo
        self.lbl_logo_preview = ctk.CTkLabel(logo_area, text="Nenhuma logo inserida",
                                              font=("Segoe UI", 13), text_color=cores.COR_TEXTO2,
                                              fg_color=cores.COR_CARD, corner_radius=8,
                                              width=200, height=200)
        self.lbl_logo_preview.pack(side="left", padx=(0, 15))

        if os.path.exists(self._logo_escola_path):
            try:
                img = ctk.CTkImage(Image.open(self._logo_escola_path), size=(200, 200))
                self._logo_ctk = img
                self.lbl_logo_preview.configure(image=img, text="")
            except:
                pass

        # Botões de logo
        botoes_logo = ctk.CTkFrame(logo_area, fg_color="transparent")
        botoes_logo.pack(side="left", anchor="n")

        ctk.CTkButton(
            botoes_logo, text="Inserir Logo", width=160, height=40,
            fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=self._inserir_logo
        ).pack(pady=(0, 8))

        ctk.CTkButton(
            botoes_logo, text="Remover Logo", width=160, height=40,
            fg_color=cores.COR_PERIGO, hover_color=cores.COR_PERIGO,
            font=("Segoe UI", 13, "bold"),
            command=self._remover_logo
        ).pack()

        # === CARD: BANCO DE DADOS ===
        db_card = criar_card(scroll)
        db_card.pack(fill="x", pady=(0, 15))

        criar_label(db_card, "BANCO DE DADOS", font=("Segoe UI", 20, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        db_frame = ctk.CTkFrame(db_card, fg_color="transparent")
        db_frame.pack(fill="x", padx=20, pady=(0, 15))
        db_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        criar_label(db_frame, "Host", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=0, column=0, sticky="w", padx=20, pady=(0, 3))
        self.entry_db_host = criar_entry(db_frame, height=38)
        self.entry_db_host.insert(0, self.valores['DB_HOST'])
        self.entry_db_host.grid(row=1, column=0, padx=20, sticky="ew")

        criar_label(db_frame, "Usuário", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=0, column=1, sticky="w", padx=20, pady=(0, 3))
        self.entry_db_user = criar_entry(db_frame, height=38)
        self.entry_db_user.insert(0, self.valores['DB_USER'])
        self.entry_db_user.grid(row=1, column=1, padx=20, sticky="ew")

        criar_label(db_frame, "Senha", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=2, column=0, sticky="w", padx=20, pady=(12, 3))
        self.entry_db_password = criar_entry(db_frame, height=38, show="*")
        self.entry_db_password.insert(0, self.valores['DB_PASSWORD'])
        self.entry_db_password.grid(row=3, column=0, padx=20, sticky="ew")

        criar_label(db_frame, "Banco", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=2, column=1, sticky="w", padx=20, pady=(12, 3))
        self.entry_db_name = criar_entry(db_frame, height=38)
        self.entry_db_name.insert(0, self.valores['DB_NAME'])
        self.entry_db_name.grid(row=3, column=1, padx=20, sticky="ew")

        # === CARD: USUÁRIO PADRÃO ===
        user_card = criar_card(scroll)
        user_card.pack(fill="x", pady=(0, 15))

        criar_label(user_card, "USUÁRIO PADRÃO", font=("Segoe UI", 20, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        user_frame = ctk.CTkFrame(user_card, fg_color="transparent")
        user_frame.pack(fill="x", padx=20, pady=(0, 15))
        user_frame.grid_columnconfigure((0, 1), weight=1, uniform="col")

        criar_label(user_frame, "Usuário", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=0, column=0, sticky="w", padx=20, pady=(0, 3))
        self.entry_default_user = criar_entry(user_frame, height=38)
        self.entry_default_user.insert(0, self.valores['DEFAULT_USER'])
        self.entry_default_user.grid(row=1, column=0, padx=20, sticky="ew")

        criar_label(user_frame, "Senha", font=("Segoe UI", 15, "bold"), text_color=cores.COR_TEXTO).grid(row=0, column=1, sticky="w", padx=20, pady=(0, 3))
        self.entry_default_password = criar_entry(user_frame, height=38, show="*")
        self.entry_default_password.insert(0, self.valores['DEFAULT_PASSWORD'])
        self.entry_default_password.grid(row=1, column=1, padx=20, sticky="ew")

        # === CARD: TURMAS ===
        turmas_card = criar_card(scroll)
        turmas_card.pack(fill="x", pady=(0, 15))

        criar_label(turmas_card, "TURMAS", font=("Segoe UI", 20, "bold"), text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        add_frame = ctk.CTkFrame(turmas_card, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=(0, 8))

        self.entry_turma_codigo = criar_entry(add_frame, placeholder="Código (ex: 3001)", width=160, height=36)
        self.entry_turma_codigo.pack(side="left", padx=(0, 8))

        self.combo_turno = criar_combo(
            add_frame, values=["Manhã", "Tarde", "Noite", "Integral"], width=140, height=36,
            button_color=cores.COR_AZUL_PRINCIPAL, button_hover_color=cores.COR_AZUL_HOVER
        )
        self.combo_turno.set("Manhã")
        self.combo_turno.pack(side="left", padx=(0, 8))

        ctk.CTkButton(
            add_frame, text="+ Adicionar", width=110, height=36,
            fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
            font=("Segoe UI", 13, "bold"),
            command=self._adicionar_turma
        ).pack(side="left")

        self.frame_lista_turmas = ctk.CTkFrame(turmas_card, fg_color="transparent")
        self.frame_lista_turmas.pack(fill="x", padx=20, pady=(0, 12))
        self._renderizar_turmas()

    def _inserir_logo(self):
        caminho = filedialog.askopenfilename(
            filetypes=[("Imagens", "*.png *.jpg *.jpeg *.gif *.bmp")],
            title="Selecionar Logo da Escola"
        )
        if not caminho:
            return
        try:
            if not os.path.exists(self._assets_dir):
                os.makedirs(self._assets_dir)
            shutil.copy2(caminho, self._logo_escola_path)
            img = ctk.CTkImage(Image.open(self._logo_escola_path), size=(200, 200))
            self._logo_ctk = img
            self.lbl_logo_preview.configure(image=img, text="")
            self._notificar("Logo inserida com sucesso!")
        except Exception as e:
            self._notificar(f"Erro ao inserir logo: {e}")

    def _remover_logo(self):
        if not os.path.exists(self._logo_escola_path):
            self._notificar("Nenhuma logo para remover.")
            return
        try:
            os.remove(self._logo_escola_path)
            self._logo_ctk = None
            self.lbl_logo_preview.configure(image=None, text="Nenhuma logo inserida")
            self._notificar("Logo removida com sucesso!")
        except Exception as e:
            self._notificar(f"Erro ao remover logo: {e}")

    def _renderizar_turmas(self):
        for w in self.frame_lista_turmas.winfo_children():
            w.destroy()
        turmas = listar_turmas()
        if not turmas:
            criar_label(self.frame_lista_turmas, "Nenhuma turma cadastrada.",
                        text_color=self.cor_texto2, font=("Segoe UI", 13)).pack(anchor="w")
            return
        for tid, codigo, turno in turmas:
            row = ctk.CTkFrame(self.frame_lista_turmas, fg_color="transparent")
            row.pack(fill="x", pady=2)
            criar_label(row, f"{codigo} - {turno}", text_color=cores.COR_TEXTO,
                        font=("Segoe UI", 13)).pack(side="left")
            ctk.CTkButton(
                row, text="✕", width=28, height=28,
                fg_color=cores.COR_PERIGO, text_color="#fff",
                font=("Segoe UI", 12, "bold"),
                command=lambda t=tid, c=codigo: self._remover_turma(t, c)
            ).pack(side="right")

    def _adicionar_turma(self):
        codigo = self.entry_turma_codigo.get().strip()
        turno = self.combo_turno.get()
        if not codigo:
            self._notificar("Informe o código da turma.")
            return
        ok = cadastrar_turma(codigo, turno)
        if ok:
            self.entry_turma_codigo.delete(0, "end")
            self._renderizar_turmas()
            self._notificar(f"Turma {codigo} - {turno} adicionada!")
        else:
            self._notificar("Erro: turma já existe ou código inválido.")

    def _remover_turma(self, id_turma, codigo):
        ok = excluir_turma(id_turma)
        if ok:
            self._renderizar_turmas()
            self._notificar(f"Turma {codigo} removida.")
        else:
            self._notificar(f"Não é possível remover: há usuários vinculados à turma {codigo}.")

    def _reconstruir(self):
        """Destrói e reconstrói toda a tela — usado tanto ao revisitar quanto
        ao receber notificação de troca de tema."""
        if not self.winfo_exists():
            return
        # Recalcula as cores base capturadas no __init__, pois a paleta pode
        # ter mudado (claro <-> escuro) desde a última construção.
        self.cor_bg = str(cores.COR_BG)
        self.cor_card = str(cores.COR_CARD)
        self.cor_texto = str(cores.COR_TEXTO)
        self.cor_texto2 = str(cores.COR_TEXTO2)
        self.configure(fg_color=self.cor_bg)

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
            'SCHOOL_NAME': self.entry_school_name.get().strip(),
        }

        linhas = [f"{k}={v}" for k, v in novos_valores.items()]
        with open(self._env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(linhas) + '\n')

        self._notificar("Configurações salvas com sucesso!")

    def _voltar(self):
        self.controller.voltar()

    def _notificar(self, mensagem):
        self.lbl_notificacao.configure(text=mensagem, text_color=cores.COR_AZUL_HOVER)
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))