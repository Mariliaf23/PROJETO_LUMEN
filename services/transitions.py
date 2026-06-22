def transicao_sair(janela, callback=None, duracao=150):
    if callback:
        callback()


def transicao_entrar(janela, duracao=150):
    pass


def navegar_com_transicao(tela_atual, controller, nome_tela):
    controller.navegar_para(nome_tela)
