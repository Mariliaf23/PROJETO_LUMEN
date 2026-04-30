<p align="center">
  <img src="assets/LUMEN logo.png" alt="Lumen Logo Original" width="200">
</p>


# PROJETO LUMEN


# 💡 PROJETO LUMEN

> **Status do Projeto:** 🚀 Em Desenvolvimento

O **Projeto Lumen** é uma aplicação desktop multiplataforma focada no gerenciamento centralizado de processos empresariais. O sistema automatiza o controle de acessos, cadastro de ativos e gestão de clientes, garantindo segurança e integridade através de um banco de dados relacional.

---

## 🛠️ Especificações Técnicas

O projeto utiliza tecnologias modernas de desenvolvimento Python para garantir performance e uma estética atual:

*   **Linguagem:** `Python 3.x`
*   **Interface Gráfica:** `CustomTkinter` (Interface moderna com suporte nativo a Dark Mode)
*   **Banco de Dados:** `MySQL`
*   **Relatórios:** `FPDF` (Exportação profissional em PDF)

---

## ⚙️ Funcionalidades e Módulos

### 🔒 Segurança e Acesso
*   **Módulo de Login:** Autenticação segura com diferenciação entre níveis de permissão (**Administrador** vs. **Operador**).
*   **Gestão de Acessos:** CRUD completo para controle de usuários do sistema.

### 👥 Gestão de Negócio
*   **CRM (Clientes):** Ciclo completo de cadastro, consulta, edição e exclusão de clientes.
*   **Inventário:** Gestão de produtos e serviços comercializados.
*   **Operacional:** Sistema de **Ordens de Serviço** ou **Vendas**, vinculando clientes a produtos/serviços de forma dinâmica.

### 📄 Inteligência de Dados
*   **Gerador de Relatórios:** Interface dedicada para filtragem de dados e exportação automatizada.
*   **Validações Rigorosas:**
    *   Impedimento de campos vazios.
    *   Máscaras para e-mail e telefone.
    *   Bloqueio de registros duplicados via Banco de Dados.

---

## 🖼️ Arquitetura da Interface

O design foi planejado para uma navegação fluida dividida em:

1.  **Tela de Login:** Portal de acesso restrito.
2.  **Dashboard Central:** Menu lateral intuitivo com acesso rápido aos módulos e indicadores.
3.  **Módulo de Relatórios:** Painel focado em exportação e análise de dados.

---

## 📂 Estrutura do Repositório

Seguindo padrões de organização avançada para escalabilidade:

```text
PROJETO_LUMEN/
├── main.py                # Ponto de entrada da aplicação
├── database_config.py     # Configurações de conexão MySQL
├── styles.py              # Identidade visual (cores e fontes)
├── services/              # Business Logic (validações e PDF)
└── screens/               # Views (Login, Home, Cadastros)
```

---

## 🚀 Como Executar (Em breve)

*Instruções para instalação de dependências e configuração do banco de dados.*