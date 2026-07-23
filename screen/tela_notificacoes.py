# tela_notificacoes.py — Central de Notificações do sistema LUMEN

import os
import sys
from PIL import Image

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk

from services.styles import (
    cores,
    criar_entry, criar_label, criar_titulo, criar_card, criar_combo, criar_botao_preenchido,
)
from services.notificacoes import (
    EVENTOS, carregar_config, salvar_config, carregar_templates, salvar_templates,
    resetar_templates, carregar_historico, limpar_historico, testar_whatsapp,
)




class TelaNotificacoes(ctk.CTkFrame):
    """Tela principal da Central de Notificações."""

    def __init__(self, master=None, controller=None):
        super().__init__(master, fg_color=cores.COR_BG)
        self.controller = controller
        self._aba_atual = "dashboard"
        self._config = carregar_config()
        self._templates = carregar_templates()
        self._construir_ui()



    def _reconstruir_tema(self):
        """Reconstrói a tela ao trocar o tema claro/escuro."""
        if not self.winfo_exists():
            return
        for widget in self.winfo_children():
            widget.destroy()
        self.configure(fg_color=cores.COR_BG)
        self._construir_ui()

    def _ao_visitar(self):
        self._config = carregar_config()
        self._templates = carregar_templates()
        self._recarregar_aba()

    # ═══════════════════════════════════════════════════════════════════════
    # UI PRINCIPAL
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=cores.COR_CARD)
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=(15, 8))

        header_left = ctk.CTkFrame(header, fg_color="transparent")
        header_left.pack(side="left", fill="y", padx=10, pady=5)

        caminho_base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(caminho_base, "assets", "logo_lumen.png")

        if os.path.exists(logo_path):
            try:
                img_logo = ctk.CTkImage(Image.open(logo_path), size=(55, 55))
                ctk.CTkLabel(header_left, image=img_logo, text="").pack(side="left", padx=(0, 15))
            except Exception:
                criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))
        else:
            criar_titulo(header_left, "LUMEN", font=("Cinzel", 22, "bold")).pack(side="left", padx=(0, 10))

        criar_label(header_left, "Central de Notificações",
                    font=("Segoe UI", 24, "bold"), text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            header, text="Voltar", command=self._voltar, width=100, height=36,
            fg_color=cores.COR_SIDEBAR, text_color="#FFFFFF", border_color=cores.COR_INPUT_BORDER, border_width=1,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=15, pady=5)

        # Abas
        abas_container = ctk.CTkFrame(self, fg_color="transparent")
        abas_container.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 5))

        self._botoes_abas = []
        abas = [
            ("Dashboard", "dashboard"),
            ("Configurações", "configuracoes"),
            ("Eventos", "eventos"),
            ("Templates", "templates"),
            ("Histórico", "historico"),
        ]

        for nome, tag in abas:
            is_atual = (tag == self._aba_atual)
            btn = ctk.CTkButton(
                abas_container, text=nome, font=("Segoe UI", 11, "bold"),
                fg_color=cores.COR_AZUL_PRINCIPAL if is_atual else cores.COR_INPUT_BG,
                text_color="#FFFFFF" if is_atual else cores.COR_TEXTO2,
                border_color=cores.COR_AZUL_PRINCIPAL if is_atual else cores.COR_INPUT_BORDER,
                border_width=1 if is_atual else 0,
                hover_color=cores.COR_AZUL_HOVER,
                width=110, height=30,
                command=lambda n=tag: self._trocar_aba(n)
            )
            btn.pack(side="left", padx=(0, 3))
            self._botoes_abas.append((btn, tag))

        # Container de conteúdo
        self._frame_conteudo = ctk.CTkFrame(self, fg_color=cores.COR_BG)
        self._frame_conteudo.grid(row=2, column=0, sticky="nsew", padx=30, pady=(5, 20))
        self._frame_conteudo.grid_columnconfigure(0, weight=1)
        self._frame_conteudo.grid_rowconfigure(0, weight=1)

        self._frames = {}
        for tag in [t[1] for t in abas]:
            frame = ctk.CTkFrame(self._frame_conteudo, fg_color=cores.COR_BG)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_rowconfigure(0, weight=1)
            self._frames[tag] = frame

        self._construir_aba_dashboard()
        self._construir_aba_configuracoes()
        self._construir_aba_eventos()
        self._construir_aba_templates()
        self._construir_aba_historico()

        self.lbl_notificacao = criar_label(self, "", text_color=cores.COR_TEXTO2)
        self._trocar_aba("dashboard")

    def _trocar_aba(self, nome):
        self._aba_atual = nome
        for btn, n in self._botoes_abas:
            if n == nome:
                btn.configure(fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                              border_color=cores.COR_AZUL_PRINCIPAL, border_width=1)
            else:
                btn.configure(fg_color=cores.COR_INPUT_BG, text_color=cores.COR_TEXTO2,
                              border_color=cores.COR_INPUT_BORDER, border_width=0)

        for tag, frame in self._frames.items():
            frame.grid_forget()

        if nome in self._frames:
            self._frames[nome].grid(row=0, column=0, sticky="nsew")

        self._recarregar_aba()

    def _recarregar_aba(self):
        if self._aba_atual == "dashboard":
            self._atualizar_dashboard()
        elif self._aba_atual == "historico":
            self._atualizar_historico()

    def _voltar(self):
        if self.controller:
            self.controller.voltar()

    def _notificar(self, msg, cor=None):
        self.lbl_notificacao.configure(text=msg, text_color=cor or cores.COR_DOURADO)
        self.lbl_notificacao.place(relx=0.5, rely=0.97, anchor="center")
        self.lbl_notificacao.bind("<Button-1>", lambda e: self.lbl_notificacao.configure(text=""))
        self.after(5000, lambda: self.lbl_notificacao.configure(text=""))

    # ═══════════════════════════════════════════════════════════════════════
    # ABA DASHBOARD
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_dashboard(self):
        frame = self._frames["dashboard"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Status geral
        self._frame_status = criar_card(frame)
        self._frame_status.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        status_inner = ctk.CTkFrame(self._frame_status, fg_color="transparent")
        status_inner.pack(fill="x", padx=20, pady=15)

        self._lbl_status_geral = criar_label(status_inner, "", font=("Segoe UI", 16, "bold"), text_color=cores.COR_TEXTO)
        self._lbl_status_geral.pack(side="left")

        self._btn_toggle = ctk.CTkButton(
            status_inner, text="", width=140, height=36,
            font=("Segoe UI", 12, "bold"),
            command=self._toggle_notificacoes
        )
        self._btn_toggle.pack(side="right")

        # Cards de resumo
        cards_frame = ctk.CTkFrame(frame, fg_color="transparent")
        cards_frame.grid(row=1, column=0, sticky="nsew")
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self._lbl_cards = []
        titulos = ["Eventos Ativos", "Enviadas Hoje", "Último Envio"]
        for i, titulo in enumerate(titulos):
            card = criar_card(cards_frame)
            card.grid(row=0, column=i, padx=5, pady=5, sticky="nsew")

            criar_label(card, titulo.upper(), font=("Segoe UI", 11, "bold"), text_color=cores.COR_TEXTO2).pack(
                anchor="w", padx=15, pady=(15, 5))
            lbl_valor = criar_label(card, "—", font=("Segoe UI", 28, "bold"), text_color=cores.COR_DOURADO)
            lbl_valor.pack(anchor="w", padx=15, pady=(0, 15))
            self._lbl_cards.append(lbl_valor)

        self._atualizar_dashboard()

    def _atualizar_dashboard(self):
        cfg = self._config
        habilitado = cfg.get("habilitado", True)
        eventos_hab = cfg.get("eventos_habilitados", {})
        total_eventos = sum(1 for v in eventos_hab.values() if v)

        self._lbl_status_geral.configure(
            text="🟢 Notificações ativas" if habilitado else "🔴 Notificações desabilitadas",
            text_color=cores.COR_SUCESSO if habilitado else cores.COR_PERIGO
        )
        self._btn_toggle.configure(
            text="Desabilitar" if habilitado else "Habilitar",
            fg_color=cores.COR_PERIGO if habilitado else cores.COR_SUCESSO,
        )

        historico = carregar_historico()
        hoje = __import__("datetime").datetime.now().strftime("%d/%m/%Y")
        enviadas_hoje = sum(1 for h in historico if h.get("data") == hoje and h.get("status") == "Enviado")
        ultimo = historico[0] if historico else None
        ultimo_texto = f"{ultimo['data']} {ultimo['hora']}" if ultimo else "—"

        self._lbl_cards[0].configure(text=str(total_eventos))
        self._lbl_cards[1].configure(text=str(enviadas_hoje))
        self._lbl_cards[2].configure(text=ultimo_texto, font=("Segoe UI", 14, "bold"))

    def _toggle_notificacoes(self):
        self._config["habilitado"] = not self._config.get("habilitado", True)
        salvar_config(self._config)
        status = "ativadas" if self._config["habilitado"] else "desabilitadas"
        self._notificar(f"Notificações {status}.")
        self._atualizar_dashboard()

    # ═══════════════════════════════════════════════════════════════════════
    # ABA CONFIGURAÇÕES
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_configuracoes(self):
        frame = self._frames["configuracoes"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Seção Geral
        card_geral = criar_card(frame)
        card_geral.grid(row=0, column=0, sticky="ew", pady=(0, 10), padx=5)

        criar_label(card_geral, "CONFIGURAÇÕES GERAIS", font=("Segoe UI", 14, "bold"),
                    text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        self._chk_habilitado_var = ctk.BooleanVar(value=self._config.get("habilitado", True))
        self._chk_abrir_var = ctk.BooleanVar(value=self._config.get("abrir_automatico", True))
        self._chk_historico_var = ctk.BooleanVar(value=self._config.get("registrar_historico", True))
        self._chk_resumo_var = ctk.BooleanVar(value=self._config.get("incluir_resumo", True))

        checks = [
            (self._chk_habilitado_var, "Habilitar notificações por WhatsApp"),
            (self._chk_abrir_var, "Abrir automaticamente o WhatsApp Web"),
            (self._chk_historico_var, "Registrar histórico de notificações"),
            (self._chk_resumo_var, "Incluir resumo da situação do usuário"),
        ]

        for var, texto in checks:
            ctk.CTkCheckBox(
                card_geral, text=texto, variable=var,
                font=("Segoe UI", 13), text_color=cores.COR_TEXTO,
                fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
                command=self._salvar_configuracoes
            ).pack(anchor="w", padx=20, pady=4)

        # Seção Teste
        card_teste = criar_card(frame)
        card_teste.grid(row=1, column=0, sticky="ew", pady=(0, 10), padx=5)

        criar_label(card_teste, "TESTAR WHATSAPP", font=("Segoe UI", 14, "bold"),
                    text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        teste_frame = ctk.CTkFrame(card_teste, fg_color="transparent")
        teste_frame.pack(fill="x", padx=20, pady=(0, 15))

        self._entry_teste_telefone = criar_entry(teste_frame, placeholder="Telefone (ex: 11987654321)", width=280, height=40)
        self._entry_teste_telefone.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            teste_frame, text="📱 Testar WhatsApp", width=180, height=40,
            fg_color=cores.COR_SUCESSO, text_color="#FFFFFF",
            hover_color=cores.COR_SUCESSO, font=("Segoe UI", 13, "bold"),
            command=self._teste_whatsapp
        ).pack(side="left")

    def _salvar_configuracoes(self):
        self._config["habilitado"] = self._chk_habilitado_var.get()
        self._config["abrir_automatico"] = self._chk_abrir_var.get()
        self._config["registrar_historico"] = self._chk_historico_var.get()
        self._config["incluir_resumo"] = self._chk_resumo_var.get()
        salvar_config(self._config)
        self._notificar("Configurações salvas!")

    def _teste_whatsapp(self):
        telefone = self._entry_teste_telefone.get().strip()
        if not telefone:
            self._notificar("Informe um número de telefone.", cores.COR_PERIGO)
            return
        sucesso, resultado = testar_whatsapp(telefone)
        if sucesso:
            self._notificar("WhatsApp Web aberto! Verifique o navegador.", cores.COR_SUCESSO)
        else:
            self._notificar(f"Erro: {resultado}", cores.COR_PERIGO)

    # ═══════════════════════════════════════════════════════════════════════
    # ABA EVENTOS
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_eventos(self):
        frame = self._frames["eventos"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        card = criar_card(frame)
        card.grid(row=0, column=0, sticky="nsew", padx=5)

        criar_label(card, "EVENTOS DE NOTIFICAÇÃO", font=("Segoe UI", 14, "bold"),
                    text_color=cores.COR_TEXTO).pack(anchor="w", padx=20, pady=(15, 10))

        criar_label(card, "Habilite ou desabilite notificações para cada tipo de evento:",
                    font=("Segoe UI", 12), text_color=cores.COR_TEXTO2).pack(anchor="w", padx=20, pady=(0, 10))

        self._chk_eventos = {}
        eventos_hab = self._config.get("eventos_habilitados", {})

        for chave, nome in EVENTOS.items():
            var = ctk.BooleanVar(value=eventos_hab.get(chave, True))
            self._chk_eventos[chave] = var

            row_frame = ctk.CTkFrame(card, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=2)

            ctk.CTkCheckBox(
                row_frame, text=nome, variable=var,
                font=("Segoe UI", 13), text_color=cores.COR_TEXTO,
                fg_color=cores.COR_AZUL_PRINCIPAL, hover_color=cores.COR_AZUL_HOVER,
                command=lambda k=chave: self._toggle_evento(k)
            ).pack(side="left")

        # Botão salvar
        ctk.CTkButton(
            card, text="Salvar Alterações", width=200, height=40,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 13, "bold"),
            command=self._salvar_eventos
        ).pack(anchor="w", padx=20, pady=(20, 15))

    def _toggle_evento(self, chave):
        pass  # Salva apenas ao clicar no botão

    def _salvar_eventos(self):
        eventos_hab = {}
        for chave, var in self._chk_eventos.items():
            eventos_hab[chave] = var.get()
        self._config["eventos_habilitados"] = eventos_hab
        salvar_config(self._config)
        self._notificar("Eventos atualizados!")

    # ═══════════════════════════════════════════════════════════════════════
    # ABA TEMPLATES
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_templates(self):
        frame = self._frames["templates"]
        frame.grid_columnconfigure(0, weight=1)

        # Scroll para múltiplos templates
        scroll = ctk.CTkScrollableFrame(frame, fg_color="transparent")
        scroll.grid(row=0, column=0, sticky="nsew")

        # Header com info de variáveis
        info_card = criar_card(scroll)
        info_card.pack(fill="x", pady=(0, 10), padx=5)

        criar_label(info_card, "VARIÁVEIS DISPONÍVEIS", font=("Segoe UI", 13, "bold"),
                    text_color=cores.COR_TEXTO).pack(anchor="w", padx=15, pady=(12, 5))

        variaveis_texto = "{nome}  {livro}  {patrimonio}  {emprestimo}  {devolucao}  {resumo}"
        criar_label(info_card, variaveis_texto, font=("Consolas", 11),
                    text_color=cores.COR_DOURADO).pack(anchor="w", padx=15, pady=(0, 12))

        self._entry_templates = {}

        for chave, nome in EVENTOS.items():
            card = criar_card(scroll)
            card.pack(fill="x", pady=(0, 8), padx=5)

            criar_label(card, nome.upper(), font=("Segoe UI", 12, "bold"),
                        text_color=cores.COR_TEXTO).pack(anchor="w", padx=15, pady=(12, 5))

            txt_edit = ctk.CTkTextbox(
                card, height=120, font=("Consolas", 11),
                fg_color=cores.COR_INPUT_BG, text_color=cores.COR_TEXTO,
                border_color=cores.COR_INPUT_BORDER, border_width=1,
                corner_radius=8
            )
            txt_edit.pack(fill="x", padx=15, pady=(0, 10))
            txt_edit.insert("1.0", self._templates.get(chave, ""))
            self._entry_templates[chave] = txt_edit

        # Botões
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 0), padx=5)

        ctk.CTkButton(
            btn_frame, text="💾 Salvar Templates", width=200, height=40,
            fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
            hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 13, "bold"),
            command=self._salvar_templates
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            btn_frame, text="↺ Restaurar Padrão", width=200, height=40,
            fg_color=cores.COR_CARD, text_color=cores.COR_TEXTO,
            hover_color=cores.COR_INPUT_BG, font=("Segoe UI", 13, "bold"),
            command=self._resetar_templates
        ).pack(side="left")

    def _salvar_templates(self):
        novos = {}
        for chave, txt_box in self._entry_templates.items():
            novos[chave] = txt_box.get("1.0", "end-1c").strip()
        self._templates = novos
        salvar_templates(novos)
        self._notificar("Templates salvos!")

    def _resetar_templates(self):
        self._templates = resetar_templates()
        for chave, txt_box in self._entry_templates.items():
            txt_box.delete("1.0", "end")
            txt_box.insert("1.0", self._templates.get(chave, ""))
        self._notificar("Templates restaurados para o padrão.")

    # ═══════════════════════════════════════════════════════════════════════
    # ABA HISTÓRICO
    # ═══════════════════════════════════════════════════════════════════════

    def _construir_aba_historico(self):
        frame = self._frames["historico"]
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        # Filtros
        filtro_card = criar_card(frame)
        filtro_card.grid(row=0, column=0, sticky="ew", pady=(0, 10), padx=5)

        filtro = ctk.CTkFrame(filtro_card, fg_color="transparent")
        filtro.pack(fill="x", padx=15, pady=10)

        criar_label(filtro, "Buscar:", font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 5))
        self._entry_hist_busca = criar_entry(filtro, placeholder="Nome do usuário...", width=200, height=30)
        self._entry_hist_busca.pack(side="left", padx=(0, 10))
        self._entry_hist_busca.bind("<KeyRelease>", lambda e: self._filtrar_historico())

        self._combo_hist_evento = criar_combo(
            filtro, values=["Todos"] + list(EVENTOS.values()),
            width=180, height=30
        )
        self._combo_hist_evento.set("Todos")
        self._combo_hist_evento.configure(command=lambda _: self._filtrar_historico())
        self._combo_hist_evento.pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filtro, text="Limpar", width=70, height=30,
            fg_color=cores.COR_CARD, font=("Segoe UI", 11),
            command=self._limpar_filtros_hist
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            filtro, text="🗑 Limpar Histórico", width=140, height=30,
            fg_color=cores.COR_PERIGO, font=("Segoe UI", 11, "bold"),
            command=self._limpar_historico
        ).pack(side="right")

        # Tabela
        self._frame_hist_tabela = ctk.CTkScrollableFrame(frame, fg_color=cores.COR_CARD, corner_radius=12,
                                                          border_width=1, border_color=cores.COR_INPUT_BORDER)
        self._frame_hist_tabela.grid(row=1, column=0, sticky="nsew", padx=5)

        self._atualizar_historico()

    def _atualizar_historico(self, dados=None):
        if dados is None:
            dados = carregar_historico()

        for w in self._frame_hist_tabela.winfo_children():
            w.destroy()

        # Header da tabela
        colunas = ["Data", "Hora", "Usuário", "Evento", "Telefone", "Status", "Observações"]
        larguras = [80, 70, 150, 150, 120, 80, 200]

        header_frame = ctk.CTkFrame(self._frame_hist_tabela, fg_color=cores.COR_BG, corner_radius=0)
        header_frame.pack(fill="x")

        for i, (col, larg) in enumerate(zip(colunas, larguras)):
            ctk.CTkLabel(header_frame, text=col, font=("Segoe UI", 11, "bold"),
                         text_color=cores.COR_TEXTO, width=larg, anchor="w").grid(
                row=0, column=i, padx=8, pady=8, sticky="w")

        if not dados:
            criar_label(self._frame_hist_tabela, "Nenhuma notificação registrada.",
                        font=("Segoe UI", 13)).pack(pady=30)
            return

        for idx, reg in enumerate(dados):
            cor = cores.COR_LINHA_PAR if idx % 2 == 0 else cores.COR_LINHA_IMPAR
            row = ctk.CTkFrame(self._frame_hist_tabela, fg_color=cor, corner_radius=0)
            row.pack(fill="x")

            valores = [
                reg.get("data", ""),
                reg.get("hora", ""),
                reg.get("usuario", ""),
                reg.get("evento", ""),
                reg.get("telefone", ""),
                reg.get("status", ""),
                reg.get("observacoes", ""),
            ]

            for i, (val, larg) in enumerate(zip(valores, larguras)):
                cor_status = cores.COR_SUCESSO if val == "Enviado" else (cores.COR_PERIGO if val == "Erro" else cores.COR_TEXTO)
                ctk.CTkLabel(row, text=val, font=("Segoe UI", 10),
                             text_color=cor_status if i == 5 else cores.COR_TEXTO,
                             width=larg, anchor="w").grid(
                    row=0, column=i, padx=8, pady=5, sticky="w")

    def _filtrar_historico(self):
        termo = self._entry_hist_busca.get().strip().lower()
        evento_filtro = self._combo_hist_evento.get()

        dados = carregar_historico()

        if termo:
            dados = [d for d in dados if termo in d.get("usuario", "").lower()]

        if evento_filtro and evento_filtro != "Todos":
            dados = [d for d in dados if d.get("evento") == evento_filtro]

        self._atualizar_historico(dados)

    def _limpar_filtros_hist(self):
        self._entry_hist_busca.delete(0, "end")
        self._combo_hist_evento.set("Todos")
        self._atualizar_historico()

    def _limpar_historico(self):
        limpar_historico()
        self._atualizar_historico()
        self._notificar("Histórico limpo.")