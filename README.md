# 🏗 Sistema da Central de Relacionamento – NOVACAP

Este sistema foi desenvolvido para atender à Central de Relacionamento (CR) da Companhia Urbanizadora da Nova Capital (NOVACAP), com o objetivo de registrar, acompanhar, tramitar e exportar processos internos e protocolos de atendimento ao cidadão e às Regiões Administrativas do DF.

---

## ⚙️ Tecnologias utilizadas

- Python 3.11+
- Flask
- SQLAlchemy
- Flask-Migrate
- HTML + CSS (Flexbox)
- SQLite (temporário para testes)
- MySQL (futuramente)
- Git + GitHub

---

## 🧱 Estrutura do projeto

cr_novacap/ ├── app/ │ ├── static/ │ ├── templates/ │ ├── routes/ │ ├── models/ │ ├── controllers/ │ ├── utils/ │ └── init.py ├── scripts/ ├── tests/ ├── docs/ ├── wiki/ ├── venv/ # não versionado ├── cr_novacap.db # banco local SQLite (gerado automaticamente) ├── run.py ├── requirements.txt ├── .env.example └── README.md

---

## 🚀 Como rodar localmente

```bash
git clone https://github.com/PadawanXXVI/cr_novacap.git
cd cr_novacap

# Criar ambiente virtual
python -m venv venv
source venv/Scripts/activate  # (Windows Git Bash)

# Instalar dependências
pip install -r requirements.txt

# Criar arquivo .env a partir do modelo
cp .env.example .env

# Editar .env com sua SECRET_KEY e URL do banco de dados

## 🔑 Exemplo de .env:

FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=sua_chave_secreta_aqui
DATABASE_URL=sqlite:///cr_novacap.db

## ▶️ Para rodar a aplicação:

flask run

Acesse: http://127.0.0.1:5000/

---

## 🧭 Objetivos do sistema

Registrar e acompanhar processos internos da Central de Relacionamento

Gerar protocolos de atendimento aos cidadãos e Regiões Administrativas do DF

Facilitar a tramitação e exportação de informações

Disponibilizar dashboards internos e relatórios estratégicos

Integrar com canais como e-mail e WhatsApp futuramente

---

## 🧩 Módulos do sistema
📁 Processos administrativos
Registro, tramitação e histórico de processos internos da CR

📥 Protocolos de atendimento
Registro de atendimentos presenciais, telefônicos, e por canais digitais (e-mail, WhatsApp)

📞 Agenda de contatos e ramais
Lista interna de telefones e ramais pesquisável (atalho CTRL+L), integrada ao sistema de protocolo

📊 Dashboard e Painel Gerencial
Cards com indicadores por status, tipo de protocolo e área responsável

🧾 Exportação de relatórios
Exportação para CSV, Excel, PDF, DOCX e JSON (em desenvolvimento)

---

## 🎯 Funcionalidades
Autenticação de usuários com controle de acesso

Cadastro e atualização de processos

Registro de protocolos com canal de origem e resposta

Exportação de relatórios por período e tipo

Visualização de histórico de tramitação

Consulta de ramais internos diretamente pelo sistema

Integração futura com canais externos (WhatsApp, e-mail)

---

## 📦 Exportações suportadas
Em desenvolvimento:

📄 CSV

📊 Excel

📘 PDF

📝 DOCX

📂 JSON

---

## 📸 Capturas de tela

Esta seção será preenchida quando as interfaces estiverem implementadas.

---

## 🧪 Testes

Testes manuais em ambiente local

Checklist de funcionalidades por tela

Planejamento para testes unitários com pytest ou unittest (futuramente)

---

## 🛠️ Contribuição

Este é um sistema interno da CR/NOVACAP. Contribuições externas não são aceitas neste momento.

Se você for colaborador interno:

Solicite autorização prévia para push no repositório

Siga as diretrizes do GitHub Projects para tarefas e commits

---

## 🔐 Segurança

Senhas armazenadas com hash

Arquivo .env com SECRET_KEY e credenciais fora do Git

Acesso restrito por autenticação (em desenvolvimento)

---

## 🔄 Fluxo de desenvolvimento

Clonar o repositório

Criar ambiente virtual e instalar dependências

Rodar flask run para desenvolvimento local

Commits enviados via main

Projeto gerido por GitHub Projects (Kanban)

---

## 🧠 Referências

Flask Documentation – https://flask.palletsprojects.com/

SQLAlchemy – https://www.sqlalchemy.org/

GitHub Projects – https://docs.github.com/en/issues/planning-and-tracking-with-projects

Documentação institucional da NOVACAP

---

## 👤 Autor

Desenvolvido por Anderson de Matos Guimarães

Central de Relacionamento – NOVACAP

Brasília/DF – 2024

---

## ✅ Próximo passo:

### Mensagem de commit:

```bash
git add README.md
git commit -m "Atualiza README.md com todas as seções: módulos, funcionalidades, segurança e estrutura do projeto CR"
git push origin main
```

---