import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from services.database_config import obter_codigos_carteirinhas
from services.carteirinha import gerar_imagem_carteirinha, salvar_pdf, salvar_pdf_unico
from services.styles import cores, FONTE_TITULO, FONTE_SUBTITULO, criar_label
from services.db_async import carregar_em_fundo

LARGURA_THUMB = 344
ALTURA_THUMB = 216


class JanelaCarteirinhas(ctk.CTkToplevel):
    """Janela que mostra as carteirinhas de todos os usuários, com botão
    de imprimir individual e botão para imprimir todas em um único PDF."""

    def __init__(self, master, usuarios):
        super().__init__(master)
        self.usuarios = usuarios
        self._cartoes = []          # [(imagem, codigo, nome, tipo)]
        self._imagens_ui = {}       # referências para evitar GC das CTkImage
        self.title("Carteirinhas")
        self.geometry("980x640")
        self.configure(fg_color=cores.COR_BG)
        self.grab_set()
        self._construir()
        self._gerar()

    # ── UI ──────────────────────────────────────────────────────────────
    def _construir(self):
        topo = ctk.CTkFrame(self, fg_color="transparent")
        topo.pack(fill="x", padx=30, pady=(20, 10))

        criar_label(topo, "Carteirinhas", font=FONTE_TITULO,
                    text_color=cores.COR_TEXTO).pack(side="left")

        ctk.CTkButton(
            topo, text="Fechar", command=self.destroy,
            width=110, height=40,
            fg_color=cores.COR_CARD, font=("Segoe UI", 14, "bold")
        ).pack(side="right", padx=(10, 0))

        self.btn_imprimir_todas = ctk.CTkButton(
            topo, text="🖨 Imprimir todas em um PDF só",
            command=self._imprimir_todas,
            width=280, height=40,
            fg_color=cores.COR_DOURADO, text_color="#FFFFFF",
            hover_color=cores.COR_DOURADO_CLARO, font=("Segoe UI", 14, "bold"),
            state="disabled"
        )
        self.btn_imprimir_todas.pack(side="right", padx=(10, 0))

        self.lbl_status = criar_label(self, "Gerando carteirinhas…",
                                      text_color=cores.COR_TEXTO2)
        self.lbl_status.pack(pady=(0, 8))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    # ── geração em thread de fundo ──────────────────────────────────────
    def _gerar(self):
        carregar_em_fundo(self, self._coletar_cartoes, self._aplicar_cartoes)

    def _coletar_cartoes(self):
        """Gera as imagens das carteirinhas fora da thread da UI."""
        codigos = obter_codigos_carteirinhas() or {}
        cartoes = []
        for user_data in self.usuarios:
            id_usuario = user_data[0]
            codigo = codigos.get(id_usuario)
            if not codigo:
                continue
            imagem = gerar_imagem_carteirinha(user_data, codigo)
            nome = (user_data[1] or "").strip() or "SEM NOME"
            tipo = (user_data[5] or "outro").capitalize()
            cartoes.append((imagem, codigo, nome, tipo))
        return cartoes

    def _aplicar_cartoes(self, dados, erro):
        if not self.winfo_exists():
            return
        if erro is not None or not dados:
            self.lbl_status.configure(
                text="Erro ao gerar as carteirinhas." if erro else "Nenhum usuário."
            )
            return

        self._cartoes = dados
        self._renderizar()
        self.lbl_status.configure(
            text=f"{len(dados)} carteirinha(s) gerada(s)."
        )
        self.btn_imprimir_todas.configure(state="normal")

    def _renderizar(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()
        self._imagens_ui = {}

        for indice, (imagem, codigo, nome, tipo) in enumerate(self._cartoes):
            linha = ctk.CTkFrame(
                self.scroll, fg_color=cores.COR_CARD, corner_radius=10
            )
            linha.pack(fill="x", pady=(0, 10), padx=2)

            thumb = ctk.CTkImage(imagem, size=(LARGURA_THUMB, ALTURA_THUMB))
            self._imagens_ui[indice] = thumb
            ctk.CTkLabel(linha, image=thumb, text="").pack(
                side="left", padx=(12, 16), pady=10
            )

            info = ctk.CTkFrame(linha, fg_color="transparent")
            info.pack(side="left", fill="y", padx=(0, 10))

            criar_label(info, nome, font=("Segoe UI", 17, "bold"),
                        text_color=cores.COR_TEXTO, anchor="w").pack(anchor="w")
            criar_label(info, tipo, font=("Segoe UI", 14),
                        text_color=cores.COR_TEXTO2, anchor="w").pack(anchor="w")
            criar_label(info, f"Código: {codigo}", font=("Segoe UI", 12),
                        text_color=cores.COR_TEXTO2, anchor="w").pack(anchor="w")

            ctk.CTkButton(
                linha, text="Imprimir", width=130, height=38,
                fg_color=cores.COR_AZUL_PRINCIPAL, text_color="#FFFFFF",
                hover_color=cores.COR_AZUL_HOVER, font=("Segoe UI", 14, "bold"),
                command=lambda i=indice: self._imprimir_individual(i)
            ).pack(side="right", padx=16)

    # ── ações ───────────────────────────────────────────────────────────
    def _imprimir_individual(self, indice):
        imagem, codigo, nome, _ = self._cartoes[indice]
        try:
            caminho = salvar_pdf(imagem, codigo)
            os.startfile(caminho)
            self.lbl_status.configure(text=f"PDF de \"{nome}\" aberto.")
        except Exception as e:
            self.lbl_status.configure(text=f"Erro ao abrir PDF: {e}")

    def _imprimir_todas(self):
        if not self._cartoes:
            return
        try:
            caminho = salvar_pdf_unico(
                [(imagem, codigo) for imagem, codigo, _, _ in self._cartoes]
            )
            os.startfile(caminho)
            self.lbl_status.configure(text="PDF com todas as carteirinhas aberto.")
        except Exception as e:
            self.lbl_status.configure(text=f"Erro ao gerar PDF único: {e}")