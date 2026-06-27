# transitions.py — Funções de transição entre telas (simplificadas)

def transicao_sair(janela, callback=None, duracao=150):
    """Executa um callback antes de sair da tela (transição de saída)."""
    if callback:                        # Se tem função de retorno
        callback()                      # Executa ela


def transicao_entrar(janela, duracao=150):
    """Transição de entrada na tela (vazia por enquanto)."""
    pass                                # Não faz nada ainda


def navegar_com_transicao(tela_atual, controller, nome_tela):
    """Navega para outra tela usando o controller."""
    controller.navegar_para(nome_tela)  # Pede ao controller para mudar de tela
