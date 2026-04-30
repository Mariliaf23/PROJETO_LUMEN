# PROJETO_LUMEN/
├── .github/               # Workflows e templates do GitHub
├── .venv/                 # Ambiente virtual (não versionado)
├── assets/                # Ícones, imagens e banners do projeto
├── database/              # Scripts SQL e migrações do banco
│   └── schema.sql         # Estrutura inicial das tabelas
├── screens/               # Arquivos .py para cada tela (UI)
│   ├── login_screen.py
│   ├── dashboard.py
│   └── reports_screen.py
├── services/              # Lógica de negócio e utilitários
│   ├── validator.py       # Máscaras e validações de campos
│   └── report_gen.py      # Geração de PDF com FPDF
├── .gitignore             # Arquivos para o Git ignorar (__pycache__, .env)
├── database_config.py     # Conexão com MySQL
├── main.py                # Execução principal do sistema
├── requirements.txt       # Dependências (customtkinter, mysql-connector, fpdf)
├── README.md              # Documentação principal
└── styles.py              # Definições de cores e fontes

# Dicas para o GitHub:
.gitignore: Certifique-se de incluir __pycache__/, .env e a pasta do seu ambiente virtual (.venv/ ou env/) para não poluir o repositório.

requirements.txt: Gere este arquivo usando o comando pip freeze > requirements.txt para que outros desenvolvedores possam instalar as dependências facilmente.

database/: Ter um arquivo .sql ajuda muito quem for clonar o seu projeto a entender como configurar o banco de dados MySQL necessário.

# PROJETO_LUMEN - ESTRUTURA EM CATEGORIA : FRONTEND - BACKEND

├── backend/               # O Cérebro (Lógica e Regras de Negócio)
│   ├── services/          # Validações e geração de PDF (FPDF)
│   ├── controllers/       # Faz a ponte entre as telas e o banco
│   └── models/            # Definição das estruturas de dados
├── frontend/              # A Cara (Interface do Usuário)
│   ├── assets/            # Logo oficial e ícones
│   ├── screens/           # Arquivos .py para cada tela (Login, Home, etc.)
│   └── styles.py          # Definições de cores e fontes do CustomTkinter
├── database/              # O Coração (Persistência de Dados)
│   ├── connection.py      # Script de conexão com o MySQL
│   └── schema.sql         # Script de criação das tabelas (DUMP)
├── main.py                # Ponto de entrada que inicializa o sistema
├── requirements.txt       # Lista de dependências (customtkinter, mysql-connector, fpdf)
└── .gitignore             # Ignora .venv e .env