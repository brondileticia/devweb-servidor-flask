# 🌐 Servidor Web com Flask — Desenvolvimento Web

[![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Mailgun](https://img.shields.io/badge/Mailgun-F06B66?style=flat-square&logo=mailgun&logoColor=white)](https://www.mailgun.com/)
[![IFSP](https://img.shields.io/badge/IFSP-006633?style=flat-square&logoColor=white)](https://www.ifsp.edu.br/)

Repositório destinado ao armazenamento das atividades práticas, estudos de caso e avaliações contínuas da disciplina de **Desenvolvimento Web** do curso de **Análise e Desenvolvimento de Sistemas (IFSP)**.

---

## 📌 Sobre o Projeto

O objetivo deste repositório é acompanhar a evolução prática do servidor web construído ao longo do semestre utilizando **Python e Flask**, cobrindo o ciclo completo de desenvolvimento de aplicações web backend:

- **Estrutura Básica & Templates:** Rotas HTTP, renderização dinâmica de páginas via Jinja2 e integração de arquivos estáticos (CSS/JS).
- **Formulários Web:** Captura, tratamento e validação de dados submetidos via formulários.
- **Persistência em Banco de Dados:** Modelagem e manipulação de dados na aplicação Flask com SQLAlchemy.
- **Integração de Serviços de E-mail:** Envio automático de mensagens e notificações via API do Mailgun.
- **Autenticação & Controle de Acesso:** Login, controle de sessões e segurança do usuário.
- **Arquitetura Completa:** Consolidação dos módulos em uma aplicação web estruturada e modular com Blueprints.

> 🎓 **Perfil Acadêmico:** [brondileticia](https://github.com/brondileticia)  
> 💼 **Perfil Principal & Projetos de Mercado:** [@leticiabrondi](https://github.com/leticiabrondi)

---

## 🛠️ Tecnologias & Ferramentas

- **Linguagem:** Python 3.10+
- **Framework Web:** Flask
- **Motor de Templates:** Jinja2
- **Framework CSS:** Bootstrap 5 + Bootstrap Icons (via CDN)
- **Manipulação de Datas:** Moment.js (via Flask-Moment)
- **Banco de Dados:** SQLite com SQLAlchemy (ORM)
- **Envio de E-mails:** Mailgun (API REST)
- **Cliente HTTP:** Requests
- **Autenticação:** Flask-Login
- **Deploy:** PythonAnywhere
- **Versionamento:** Git & GitHub
- **Ambiente de Aprendizagem:** AVA (Ambiente Virtual de Aprendizagem) & SUAP

---

## 📂 Estrutura do Projeto

```
flask/
├── run.py                      # Ponto de entrada da aplicação
├── config.py                   # Configurações centralizadas
├── requirements.txt            # Dependências do projeto
├── .gitignore                  # Arquivos ignorados pelo Git
├── app/
│   ├── __init__.py             # Factory da aplicação + registro de blueprints
│   ├── models.py               # Modelos (Usuario, EmailEnviado)
│   ├── services/
│   │   └── email_service.py    # Lógica de envio e persistência de e-mails
│   ├── main/
│   │   ├── atividades.py       # Catálogo ÚNICO das atividades (home, menu e Ctrl+K)
│   │   └── routes.py           # Home (3 estados), Data/Hora, Identificação, etc.
│   ├── users/
│   │   └── routes.py           # Banco de Dados, CRUD de usuários
│   ├── emails/
│   │   └── routes.py           # Listagem de e-mails enviados
│   ├── auth/
│   │   └── routes.py           # Controle de acesso global, login, cadastro, confirmação
│   └── templates/
│       ├── base.html
│       ├── home.html
│       ├── data_hora.html
│       ├── identificacao.html
│       ├── contextorequisicao.html
│       ├── formulario_identificacao.html
│       ├── login.html
│       ├── banco_dados.html
│       ├── emails_enviados.html
│       ├── formulario.html
│       ├── user.html
│       ├── 404.html
│       └── 500.html
│   └── static/
│       ├── css/estilo.css      # Estilo global
│       └── js/app.js           # Comportamentos globais (busca, Ctrl+K, senha)
└── tests/
    └── test_acesso.py          # Testes automatizados da Semana 16
```

---

## ✨ Funcionalidades Implementadas

### Aula 040 — Fundamentos do Flask
- [x] Rotas básicas (`/`, `/user/<name>`, etc.)
- [x] Retorno de códigos de status HTTP
- [x] Criação de respostas com cookies (`make_response`)
- [x] Redirecionamento (`redirect`) e aborto (`abort`)
- [x] Templates com Jinja2
- [x] Herança de templates (`base.html`)
- [x] Integração com Bootstrap
- [x] Formatação de datas com Moment.js

### Aula 050.B — Formulários e Sessões
- [x] Formulário de identificação do aluno
- [x] Persistência de dados em sessão
- [x] Flash messages para feedback
- [x] Página de login com validação simples
- [x] Detecção de mudança de nome no formulário

### Semana 07/08 — Banco de Dados
- [x] Modelo `Usuario` com SQLAlchemy
- [x] Persistência em SQLite
- [x] CRUD completo (Create, Read, Update, Delete)
- [x] Associação de funções aos usuários

### Semana 09 — Múltiplas Funções
- [x] Três funções: `User`, `Moderator`, `Administrator`
- [x] Ciclo de promoção/rebaixamento
- [x] Listagem agrupada por função
- [x] Contadores de usuários e funções
- [x] Estatísticas por função

### Semana 10/11 — Envio de E-mails
- [x] Integração com Mailgun (API REST)
- [x] Envio automático ao cadastrar usuário
- [x] E-mail institucional (sempre)
- [x] E-mail do professor (opcional via checkbox)
- [x] Corpo do e-mail com prontuário, nome do aluno e usuário cadastrado

### Semana 12 — Persistência de E-mails
- [x] Modelo `EmailEnviado` com SQLAlchemy
- [x] Persistência de todos os envios (sucesso e falha)
- [x] Página `/emailsEnviados` com listagem
- [x] Contadores de e-mails enviados
- [x] Histórico com data/hora e status

### Semana 13 — E-mail Adicional + Estrutura Modular
- [x] Campo de e-mail adicional no formulário
- [x] Validação de e-mail com regex
- [x] Estrutura modular com Blueprints
- [x] Factory Pattern (`create_app`)
- [x] Separação por módulos: `main`, `users`, `emails`, `auth`
- [x] Serviço de e-mail isolado (`email_service.py`)

### Semana 16 — Autenticação vinculada à apresentação de informações
- [x] Home com 3 estados: anônimo, logado sem confirmar e logado confirmado
- [x] Anônimo vê apenas **"Olá, Desconhecido!"** — sem menu e sem acesso a nenhuma página
- [x] Usuário não confirmado consegue entrar, mas recebe o aviso de que não pode acessar antes da confirmação
- [x] Reenvio do e-mail de confirmação (gera um token novo)
- [x] Relação de usuários cadastrados (nome, e-mail, username, confirmado) **somente** para quem está confirmado
- [x] Controle de acesso centralizado com `before_app_request` (um "porteiro" para todas as rotas)
- [x] `UsuarioAnonimo` personalizado (`current_user.nome == 'Desconhecido'`)
- [x] Lista de atividades moderna: busca instantânea, navegação por teclado e paleta de comandos **Ctrl+K**
- [x] Atividades centralizadas em `app/main/atividades.py` (antes estavam duplicadas)
- [x] JavaScript unificado em `static/js/app.js` (sem scripts repetidos nos templates)
- [x] Banco de Dados: 1 consulta em vez de 7 para montar a listagem
- [x] Testes automatizados com `unittest`

---

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

- **Python 3.10+** instalado
- **Git** instalado

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone https://github.com/brondileticia/devweb-servidor-flask.git
cd devweb-servidor-flask
```

2. **Crie e ative um ambiente virtual (`venv`):**

   **Windows:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

   **Linux/Mac:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente** (obrigatório para envio de e-mail):

   **Linux/Mac:**
   ```bash
   export SECRET_KEY="sua_chave_secreta"
   export MAILGUN_API_KEY="sua_api_key"
   export MAILGUN_DOMAIN="sandboxXXXX.mailgun.org"
   ```

   **Windows:**
   ```cmd
   set SECRET_KEY=sua_chave_secreta
   set MAILGUN_API_KEY=sua_api_key
   set MAILGUN_DOMAIN=sandboxXXXX.mailgun.org
   ```

5. **Execute o servidor:**
```bash
python run.py
```

6. **Acesse no navegador:**
```
http://127.0.0.1:5000/
```

7. **Contas de exemplo** (criadas só quando o banco está vazio):

| Usuário | Senha | Situação |
|---------|-------|----------|
| `john` | `senha1234` | Confirmado — vê a relação e as atividades |
| `susan` | `senha1234` | Não confirmado — vê apenas o aviso |

> Banco antigo? Apague o arquivo `app.db` para recriar com os exemplos.

8. **Rode os testes:**
```bash
python -m unittest -v
```

---

## 🌐 Deploy no PythonAnywhere

O projeto está configurado para deploy no **PythonAnywhere**. As variáveis de ambiente são configuradas no arquivo WSGI:

```python
import sys
import os

path = '/home/brondileticia/flask'
if path not in sys.path:
    sys.path.append(path)

os.environ['SECRET_KEY'] = 'sua_chave_secreta'
os.environ['MAILGUN_API_KEY'] = 'sua_api_key'
os.environ['MAILGUN_DOMAIN'] = 'sandboxXXXX.mailgun.org'

from app import create_app
application = create_app()
```

**Passos para atualizar:**
```bash
cd ~/flask
git pull origin main
# Web → Reload no painel do PythonAnywhere
```

---

## 📧 Configuração do Mailgun

Para o envio de e-mails funcionar, é necessário:

1. Criar conta em [mailgun.com](https://www.mailgun.com/)
2. Obter a **API Key** e o **Sandbox Domain**
3. Adicionar os e-mails de destino em **Authorized Recipients**:
   - `l.brondi@aluno.ifsp.edu.br`
   - `flaskaulasweb@zohomail.com` (o professor precisa confirmar o link recebido)
4. Configurar as variáveis de ambiente no WSGI do PythonAnywhere

---

## 🗺️ Rotas da Aplicação

| Rota | Método | Acesso | Descrição |
|------|--------|--------|-----------|
| `/` | GET | Todos | Home (conteúdo muda conforme o estado do usuário) |
| `/login` | GET/POST | Todos | Login por e-mail ou username |
| `/cadastro` | GET/POST | Todos | Criação de conta |
| `/confirmar/<token>` | GET | Todos | Confirmação do e-mail |
| `/esqueci-senha` | GET/POST | Todos | Pedido de redefinição de senha |
| `/resetar-senha/<token>` | GET/POST | Todos | Nova senha |
| `/reenviar-confirmacao` | POST | Logado | Reenvia o link de confirmação |
| `/logout` | GET | Logado | Encerra a sessão |
| `/data-hora` | GET | Confirmado | Data/hora com Moment.js |
| `/identificacao` | GET | Confirmado | Dados do aluno |
| `/contextorequisicao` | GET | Confirmado | Informações da requisição HTTP |
| `/formulario-identificacao` | GET/POST | Confirmado | Formulário de identificação |
| `/formulario` | GET/POST | Confirmado | Formulário simples com sessão |
| `/banco-dados/` | GET/POST | Confirmado | Cadastro e listagem de usuários |
| `/emailsEnviados` | GET | Confirmado | Histórico de e-mails |
| `/alterar-senha` · `/alterar-email` | GET/POST | Confirmado | Gerenciamento da conta |

---

## 📊 Modelos de Dados

### `Usuario`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `nome` | String(100) | Nome do usuário |
| `email` | String(120) | E-mail (único, opcional) |
| `username` | String(50) | Nome de usuário (único, opcional) |
| `password_hash` | String(256) | Hash da senha (nunca a senha pura) |
| `funcao` | String(50) | User, Moderator ou Administrator |
| `email_confirmado` | Boolean | Se o e-mail foi confirmado |
| `token_confirmacao` | String(100) | Token do link de confirmação |
| `token_reset` / `token_reset_expira` | String / DateTime | Redefinição de senha |
| `criado_em` / `atualizado_em` | DateTime | Datas de criação e atualização |

### `EmailEnviado`
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id` | Integer | Chave primária |
| `remetente` | String(200) | Endereço do remetente |
| `destinatarios` | Text | Lista de destinatários |
| `assunto` | String(300) | Assunto do e-mail |
| `texto` | Text | Corpo resumido |
| `enviado_em` | DateTime | Data/hora do envio |
| `sucesso` | Boolean | Se o envio foi bem-sucedido |

---

## 👩‍🎓 Autora

**Leticia Brondi Carvalheiro**  
Curso: Análise e Desenvolvimento de Sistemas — 4º Semestre  
Instituição: IFSP — Campus Pirituba  
Disciplina: PTBDSWS — Programação em Desenvolvimento Web Servidor

---

## 📝 Licença

Este projeto é de uso acadêmico e foi desenvolvido como parte das atividades da disciplina **PTBDSWS** do IFSP.
