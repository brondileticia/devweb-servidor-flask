"""
Configurações centralizadas da aplicação.
"""
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configurações base."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')
    
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    JSON_SORT_KEYS = False
    
    # Mailgun
    MAILGUN_API_KEY = os.environ.get('MAILGUN_API_KEY') or os.environ.get('API_KEY', '')
    MAILGUN_DOMAIN = os.environ.get(
        'MAILGUN_DOMAIN',
        'sandbox2ee0c97988c848cd84add8f3d62a0ac0.mailgun.org'
    )
    
    # Dados do aluno
    ALUNO_NOME = 'Leticia Brondi Carvalheiro'
    ALUNO_PRONTUARIO = 'SEU_PRONTUARIO'
    ALUNO_INSTITUICAO = 'IFSP'
    
    EMAIL_INSTITUCIONAL = 'l.brondi@aluno.ifsp.edu.br'
    EMAIL_PROFESSOR = 'flaskaulasweb@zohomail.com'
    
    # Funções disponíveis
    FUNCOES = ['User', 'Moderator', 'Administrator']
    
    HIERARQUIA_FUNCOES = {
        'Administrator': 1,
        'Moderator': 2,
        'User': 3
    }
    
    ICONES_FUNCOES = {
        'Administrator': {'icone': 'glyphicon-king', 'cor': 'danger', 'label': 'label-danger'},
        'Moderator': {'icone': 'glyphicon-eye-open', 'cor': 'warning', 'label': 'label-warning'},
        'User': {'icone': 'glyphicon-user', 'cor': 'info', 'label': 'label-info'}
    }
    
    DISCIPLINAS = ['DSWA5', 'DWBA4', 'Gestão de Projetos']
