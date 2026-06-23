<p align="center">
  <img src="assets/logo_lumen.png" alt="Lumen Logo" width="200">
</p>

# 💡 PROJETO LUMEN

> **Status do Projeto:** 🚀 Em Desenvolvimento

O **Projeto Lumen** é uma aplicação desktop multiplataforma focada no gerenciamento de uma biblioteca. O sistema automatiza o cadastro de livros, exemplares, empréstimos e devoluções, garantindo segurança e integridade através de um banco de dados relacional.

---

## 🛠️ Especificações Técnicas

O projeto utiliza tecnologias modernas de desenvolvimento Python para garantir performance e uma estética atual:

*   **Linguagem:** `Python 3.x`
*   **Interface Gráfica:** `CustomTkinter` (Interface moderna com suporte nativo a Dark Mode)
*   **Banco de Dados:** `MySQL`
*   **Relatórios:** `FPDF2` (Exportação profissional em PDF)
*   **Gráficos:** `Canvas nativo do Tkinter`
*   **Imagens:** `Pillow`
*   **Variáveis de Ambiente:** `python-dotenv`

---

## ⚙️ Funcionalidades e Módulos

### 🔒 Segurança e Acesso
*   **Módulo de Login:** Autenticação segura com diferenciação entre níveis de permissão (**Administrador** vs. **Operador**).
*   **Gestão de Acessos:** Cadastro e gerenciamento de usuários do sistema.

### 📚 Gestão Bibliotecária
*   **Livros:** Cadastro, consulta, edição e exclusão de livros.
*   **Exemplares:** Gestão de exemplares físicos de cada livro.
*   **Empréstimos:** Registro e acompanhamento de empréstimos realizados.
*   **Devoluções:** Controle de devoluções com validação de prazos.

### ⚙️ Configurações
*   **Configurações do Sistema:** Painel de configurações gerais da aplicação.

### 📄 Relatórios
*   **Gerador de Relatórios:** Interface dedicada para filtragem de dados e exportação automatizada em PDF.

---

## 🖼️ Arquitetura da Interface

O design foi planejado para uma navegação fluida dividida em:

1.  **Tela de Login:** Portal de acesso restrito.
2.  **Dashboard Central:** Menu intuitivo com acesso rápido aos módulos.
3.  **Módulos Operacionais:** Telas dedicadas para livros, exemplares, empréstimos e devoluções.

---

## 📂 Estrutura do Repositório

```text
PROJETO_LUMEN/
├── assets/                # Ícones, imagens e banners do projeto
├── database/              # Scripts SQL e migrações do banco
│   └── schema.sql         # Estrutura inicial das tabelas
├── screen/                # Arquivos .py para cada tela (UI)
│   ├── dashboard.py
│   ├── emprestimos.py
│   ├── tela_cadastro_login.py
│   ├── tela_cadastro_usuario.py
│   ├── tela_configuracoes.py
│   ├── tela_devolucoes.py
│   ├── tela_exemplares.py
│   ├── tela_livros.py
│   └── tela_login.py
├── services/              # Lógica de negócio e utilitários
│   ├── app_controller.py  # Controlador de navegação entre telas
│   ├── conector.py        # Conexão com o banco de dados
│   ├── database_config.py # Configurações do banco de dados
│   ├── report_gen.py      # Geração de PDF com FPDF2
│   ├── styles.py          # Definições de cores e fontes
│   ├── transitions.py     # Transições entre telas
│   └── validador.py       # Máscaras e validações de campos
├── .env                   # Variáveis de ambiente (não versionado)
├── .gitignore             # Arquivos para o Git ignorar (__pycache__, .env)
├── main.py                # Execução principal do sistema
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação principal
```

---

## 🚀 Como Executar

1.  **Crie um ambiente virtual:**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate  # Windows
    ```

2.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure o banco de dados:**
    *   Crie um banco de dados MySQL
    *   Execute o script `database/schema.sql` para criar as tabelas
    *   Configure as credenciais no arquivo `.env`

4.  **Execute o sistema:**
    ```bash
    python main.py
    ```
