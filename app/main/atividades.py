"""
Catálogo único das atividades do sistema.

Antes, a lista de atividades existia em DOIS lugares (base.html e main/routes.py)
e era fácil esquecer de atualizar um deles. Agora existe uma única fonte da
verdade: este arquivo. O context processor (app/__init__.py) injeta ATIVIDADES
em todos os templates — a home, o menu e a paleta de comandos (Ctrl+K) leem daqui.

Para adicionar uma atividade nova:
    1. crie a rota (ex.: @bp.route('/minha-pagina') em main/routes.py);
    2. acrescente um dicionário abaixo com o endpoint dessa rota.
"""

# Cada grupo vira uma seção na lista da home.
GRUPOS = [
    ('fundamentos', 'Fundamentos do Flask'),
    ('formularios', 'Formulários e Sessão'),
    ('dados', 'Banco de Dados e E-mails'),
]

ATIVIDADES = [
    {
        'endpoint': 'main.data_hora',
        'titulo': 'Data e Hora',
        'descricao': 'Data, hora e informações temporais com Moment.js',
        'icone': 'bi-clock',
        'cor': 'primary',
        'grupo': 'fundamentos',
        'palavras': 'moment tempo relogio',
    },
    {
        'endpoint': 'main.identificacao',
        'titulo': 'Identificação do Aluno',
        'descricao': 'Dados do aluno e do campus',
        'icone': 'bi-person-vcard',
        'cor': 'success',
        'grupo': 'fundamentos',
        'palavras': 'aluno prontuario campus',
    },
    {
        'endpoint': 'main.contextorequisicao',
        'titulo': 'Contexto da Requisição',
        'descricao': 'User-Agent, IP e host da requisição HTTP',
        'icone': 'bi-hdd-network',
        'cor': 'info',
        'grupo': 'fundamentos',
        'palavras': 'request http ip navegador',
    },
    {
        'endpoint': 'main.formulario_identificacao',
        'titulo': 'Formulário de Identificação',
        'descricao': 'Nome, instituição e disciplina guardados na sessão',
        'icone': 'bi-ui-checks',
        'cor': 'warning',
        'grupo': 'formularios',
        'palavras': 'form sessao disciplina',
    },
    {
        'endpoint': 'main.formulario',
        'titulo': 'Formulário Simples',
        'descricao': 'Padrão Post/Redirect/Get com sessão',
        'icone': 'bi-pencil-square',
        'cor': 'secondary',
        'grupo': 'formularios',
        'palavras': 'prg post redirect get',
    },
    {
        'endpoint': 'users.banco_dados',
        'titulo': 'Banco de Dados',
        'descricao': 'Usuários agrupados por função (CRUD)',
        'icone': 'bi-database',
        'cor': 'primary',
        'grupo': 'dados',
        'palavras': 'sqlalchemy crud funcao cadastro',
    },
    {
        'endpoint': 'emails.emails_enviados',
        'titulo': 'E-mails Enviados',
        'descricao': 'Histórico de e-mails enviados pelo Mailgun',
        'icone': 'bi-envelope-paper',
        'cor': 'success',
        'grupo': 'dados',
        'palavras': 'mailgun historico email',
    },
]
