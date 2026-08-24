"""
Aplicação Flask - Avaliação Contínua
Disciplina: PTBDSWS - Desenvolvimento Web Servidor
Aluno: Leticia Brondi
Instituição: IFSP - Campus Pirituba
"""

from datetime import datetime
from flask import (Flask, render_template, request, session, 
                   flash, redirect, url_for, abort, make_response)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import flask
import os

# ============ CONFIGURAÇÃO DA APLICAÇÃO ============

app = Flask(__name__)

# Chave secreta para sessões
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

# ============ DADOS DO ALUNO ============

ALUNO = {
    'nome': 'Leticia Brondi Carvalheiro',
    'prontuario': 'PT3037801',
    'instituicao': 'IFSP',
    'curso': 'Análise e Desenvolvimento de Sistemas',
    'semestre': '4º Semestre',
    'campus': 'Pirituba'
}

# Lista de disciplinas disponíveis
DISCIPLINAS = [
    'DSWA5',
    'DWBA4',
    'Gestão de Projetos'
]

# ============ CONTEXT PROCESSOR ============

@app.context_processor
def inject_globals():
    """Injeta variáveis globais em todos os templates"""
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliações contínuas, 2026'
    }

# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

# ============ ROTA HOME OFICIAL (NOVA - COM CARDS) ============

@app.route('/')
def home():
    """
    Rota Home - Página principal com cards de navegação
    """
    # Lista de páginas disponíveis
    paginas = [
        {
            'titulo': 'Data e Hora',
            'descricao': 'Visualize data, hora e informações temporais',
            'url': '/data-hora',
            'icone': 'glyphicon-time',
            'cor': 'panel-primary'
        },
        {
            'titulo': 'Identificação do Aluno',
            'descricao': 'Dados de identificação do aluno e instituição',
            'url': '/identificacao',
            'icone': 'glyphicon-user',
            'cor': 'panel-success'
        },
        {
            'titulo': 'Contexto da Requisição',
            'descricao': 'Dados técnicos da requisição HTTP',
            'url': '/contextorequisicao',
            'icone': 'glyphicon-info-sign',
            'cor': 'panel-info'
        },
        {
            'titulo': 'Formulário de Identificação',
            'descricao': 'Formulário com nome, instituição e disciplina',
            'url': '/formulario-identificacao',
            'icone': 'glyphicon-edit',
            'cor': 'panel-warning'
        },
        {
            'titulo': 'Login',
            'descricao': 'Sistema de autenticação de usuários',
            'url': '/login',
            'icone': 'glyphicon-log-in',
            'cor': 'panel-danger'
        },
        {
            'titulo': 'Formulário Simples',
            'descricao': 'Formulário básico com sessão e flash messages',
            'url': '/formulario',
            'icone': 'glyphicon-pencil',
            'cor': 'panel-default'
        }
    ]
    
    return render_template('home.html',
                         paginas=paginas,
                         current_time=datetime.utcnow(),
                         titulo='Home',
                         descricao='Página central com todas as avaliações contínuas')

# ============ ROTA DATA E HORA (ANTIGA HOME) ============

@app.route('/data-hora')
def data_hora():
    """
    Rota Data e Hora - Mostra informações temporais
    """
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora',
                         descricao='Informações temporais e demonstração de tecnologias')

# ============ ROTA FORMULÁRIO DE IDENTIFICAÇÃO (NOVA PÁGINA DA SEMANA) ============

@app.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    """
    Rota Formulário de Identificação - Recebe dados do usuário
    (Página nova da semana)
    """
    # Dados da sessão (se existirem)
    nome = session.get('nome', '')
    sobrenome = session.get('sobrenome', '')
    instituicao = session.get('instituicao', None)
    disciplina = session.get('disciplina', '')
    
    # Dados da requisição
    remote_ip = request.remote_addr or None
    host = request.host or None
    
    if request.method == 'POST':
        # Processar formulário
        nome = request.form.get('nome', '').strip()
        sobrenome = request.form.get('sobrenome', '').strip()
        instituicao = request.form.get('instituicao', '').strip()
        disciplina = request.form.get('disciplina', '').strip()
        
        # Validação básica
        if not nome or not sobrenome:
            flash('Nome e sobrenome são obrigatórios!', 'danger')
            return redirect(url_for('formulario_identificacao'))
        
        # Salvar na sessão
        session['nome'] = nome
        session['sobrenome'] = sobrenome
        session['instituicao'] = instituicao if instituicao else None
        session['disciplina'] = disciplina
        
        flash(f'Dados atualizados com sucesso! Bem-vindo(a), {nome} {sobrenome}!', 'success')
        
        # PRG Pattern
        return redirect(url_for('formulario_identificacao'))
    
    # Nome completo
    nome_completo = f"{nome} {sobrenome}".strip() if nome else None
    
    return render_template('formulario_identificacao.html',
                         nome=nome,
                         sobrenome=sobrenome,
                         nome_completo=nome_completo,
                         instituicao=instituicao,
                         disciplina=disciplina,
                         disciplinas=DISCIPLINAS,
                         remote_ip=remote_ip,
                         host=host,
                         current_time=datetime.utcnow(),
                         titulo='Formulário de Identificação',
                         descricao='Formulário completo de identificação do usuário')

# ============ ROTA LOGIN ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Rota Login - Autenticação de usuário
    """
    if request.method == 'POST':
        # Processar login
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        
        # Validação básica
        if not usuario or not senha:
            flash('Usuário e senha são obrigatórios!', 'danger')
            return redirect(url_for('login'))
        
        # Simulação de verificação (substituir por banco de dados)
        if usuario == 'admin' and senha == '123456':
            session['usuario_logado'] = usuario
            flash(f'Login realizado com sucesso! Bem-vindo(a), {usuario}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
            return redirect(url_for('login'))
    
    # GET: Mostrar formulário de login
    return render_template('login.html',
                         current_time=datetime.utcnow(),
                         titulo='Login',
                         descricao='Página de autenticação')

# ============ ROTA LOGOUT ============

@app.route('/logout')
def logout():
    """Rota para sair do sistema"""
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('home'))

# ============ ROTA IDENTIFICAÇÃO (MANTIDA) ============

@app.route('/identificacao')
def identificacao():
    """Rota Identificação - Mostra dados do aluno"""
    return render_template('identificacao.html',
                         titulo='Identificação do Aluno',
                         descricao='Dados de identificação do aluno')

# ============ ROTA CONTEXTO DA REQUISIÇÃO (MANTIDA) ============

@app.route('/contextorequisicao')
def contextorequisicao():
    """Rota Contexto da Requisição"""
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    remote_ip = request.remote_addr or 'Desconhecido'
    host = request.host or 'Desconhecido'
    
    return render_template('contextorequisicao.html',
                         user_agent=user_agent,
                         remote_ip=remote_ip,
                         host=host,
                         titulo='Contexto da Requisição',
                         descricao='Dados técnicos da requisição HTTP')

# ============ ROTA FORMULÁRIO SIMPLES (MANTIDA) ============

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    """Rota do Formulário Simples"""
    nome_atual = session.get('nome_usuario', None)
    
    if request.method == 'POST':
        novo_nome = request.form.get('nome', '').strip()
        
        if novo_nome:
            if nome_atual and nome_atual != novo_nome:
                flash(f'O nome foi alterado de "{nome_atual}" para "{novo_nome}"!', 'warning')
            else:
                flash(f'Bem-vindo(a), {novo_nome}!', 'success')
            
            session['nome_usuario'] = novo_nome
        else:
            flash(f'Nome "{nome_atual}" removido!', 'info')
            session.pop('nome_usuario', None)
        
        return redirect(url_for('formulario'))
    
    if request.args.get('limpar') == 'true':
        session.pop('nome_usuario', None)
        flash('Nome limpo com sucesso!', 'info')
        return redirect(url_for('formulario'))
    
    nome_atual = session.get('nome_usuario', None)
    
    return render_template('formulario.html',
                         nome=nome_atual,
                         titulo='Formulário Simples',
                         descricao='Formulário básico com sessão')

# ============ ROTA DINÂMICA DE USUÁRIO ============

@app.route('/user/<name>')
def user(name):
    """Rota dinâmica de usuário"""
    name = name.replace('<', '').replace('>', '').strip()
    
    if not name:
        flash('Nome inválido!', 'danger')
        return redirect(url_for('home'))
    
    return render_template('user.html',
                         name=name,
                         titulo=f'Usuário {name}',
                         descricao=f'Página personalizada para {name}')

# ============ EXECUÇÃO ============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
