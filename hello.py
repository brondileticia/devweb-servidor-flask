"""
Aplicação Flask - Avaliação Contínua: Semana 07
Disciplina: PTBDSWS - Programação em Desenvolvimento Web Servidor
Aluno: Leticia Brondi
Instituição: IFSP - Campus Pirituba
"""

from datetime import datetime
from flask import (Flask, render_template, request, session, 
                   flash, redirect, url_for, abort, make_response)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import flask
import os

# ============ CONFIGURAÇÃO DA APLICAÇÃO ============

app = Flask(__name__)

# Chave secreta para sessões
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Configuração do Banco de Dados
# SQLite para desenvolvimento local
# MySQL para produção no PythonAnywhere
if os.environ.get('PYTHONANYWHERE_SITE'):
    # Configuração para PythonAnywhere (MySQL)
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}'.format(
        username=os.environ.get('PYTHONANYWHERE_USERNAME', 'brondileticia'),
        password=os.environ.get('DB_PASSWORD', ''),
        hostname=os.environ.get('PYTHONANYWHERE_HOSTNAME', 'brondileticia.mysql.pythonanywhere-services.com'),
        databasename='brondileticia$default'
    )
else:
    # Configuração para desenvolvimento local (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# ============ MODELOS (CLASSES DE BANCO DE DADOS) ============

class Usuario(db.Model):
    """
    Classe Usuario - Representa a tabela 'usuarios' no banco de dados
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, nome):
        self.nome = nome
    
    def __repr__(self):
        return f'<Usuario {self.nome}>'
    
    def salvar(self):
        """Salva o usuário no banco de dados"""
        db.session.add(self)
        db.session.commit()
    
    def atualizar(self, novo_nome):
        """Atualiza o nome do usuário"""
        self.nome = novo_nome
        self.atualizado_em = datetime.utcnow()
        db.session.commit()
    
    def deletar(self):
        """Remove o usuário do banco de dados"""
        db.session.delete(self)
        db.session.commit()

# ============ DADOS DO ALUNO ============

ALUNO = {
    'nome': 'Leticia Brondi',
    'prontuario': 'SEU_PRONTUARIO',
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
        'app_name': 'Avaliação contínua: Semana 07'
    }

# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

# ============ ROTA HOME OFICIAL (COM CARDS) ============

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
            'cor': 'panel-primary',
            'aula': 'Aula 040'
        },
        {
            'titulo': 'Identificação do Aluno',
            'descricao': 'Dados de identificação do aluno e instituição',
            'url': '/identificacao',
            'icone': 'glyphicon-user',
            'cor': 'panel-success',
            'aula': 'Aula 040'
        },
        {
            'titulo': 'Contexto da Requisição',
            'descricao': 'Dados técnicos da requisição HTTP',
            'url': '/contextorequisicao',
            'icone': 'glyphicon-info-sign',
            'cor': 'panel-info',
            'aula': 'Aula 040'
        },
        {
            'titulo': 'Formulário de Identificação',
            'descricao': 'Formulário com nome, instituição e disciplina',
            'url': '/formulario-identificacao',
            'icone': 'glyphicon-edit',
            'cor': 'panel-warning',
            'aula': 'Aula 050.B'
        },
        {
            'titulo': 'Login',
            'descricao': 'Sistema de autenticação de usuários',
            'url': '/login',
            'icone': 'glyphicon-log-in',
            'cor': 'panel-danger',
            'aula': 'Aula 050.B'
        },
        {
            'titulo': 'Banco de Dados',
            'descricao': 'Usuários com Flask-SQLAlchemy',
            'url': '/banco-dados',
            'icone': 'glyphicon-hdd',
            'cor': 'panel-primary',
            'aula': 'Semana 07'
        },
        {
            'titulo': 'Formulário Simples',
            'descricao': 'Formulário básico com sessão e flash messages',
            'url': '/formulario',
            'icone': 'glyphicon-pencil',
            'cor': 'panel-default',
            'aula': 'Extra'
        }
    ]
    
    return render_template('home.html',
                         paginas=paginas,
                         current_time=datetime.utcnow(),
                         titulo='Home',
                         descricao='Página central com todas as atividades')

# ============ ROTA DATA E HORA ============

@app.route('/data-hora')
def data_hora():
    """Rota Data e Hora"""
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora',
                         descricao='Informações temporais e demonstração de tecnologias')

# ============ ROTA BANCO DE DADOS (NOVA - SEMANA 07) ============

@app.route('/banco-dados', methods=['GET', 'POST'])
def banco_dados():
    """
    Rota Banco de Dados - Usa SQLAlchemy para guardar nomes
    """
    if request.method == 'POST':
        # Pega o nome do formulário
        nome = request.form.get('nome', '').strip()
        
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('banco_dados'))
        
        # Verifica se já existe um usuário
        usuario_existente = Usuario.query.first()
        
        if usuario_existente:
            # Atualiza o usuário existente
            usuario_existente.atualizar(nome)
            flash(f'Nome atualizado para "{nome}"!', 'success')
        else:
            # Cria novo usuário
            novo_usuario = Usuario(nome)
            novo_usuario.salvar()
            flash(f'Usuário "{nome}" criado com sucesso!', 'success')
        
        # PRG Pattern
        return redirect(url_for('banco_dados'))
    
    # GET: Busca o último usuário
    usuario = Usuario.query.order_by(Usuario.id.desc()).first()
    
    return render_template('banco_dados.html',
                         usuario=usuario,
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados',
                         descricao='Usuários com Flask-SQLAlchemy')

# ============ ROTA FORMULÁRIO DE IDENTIFICAÇÃO ============

@app.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    """Rota Formulário de Identificação"""
    nome = session.get('nome', '')
    sobrenome = session.get('sobrenome', '')
    instituicao = session.get('instituicao', None)
    disciplina = session.get('disciplina', '')
    
    remote_ip = request.remote_addr or None
    host = request.host or None
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        sobrenome = request.form.get('sobrenome', '').strip()
        instituicao = request.form.get('instituicao', '').strip()
        disciplina = request.form.get('disciplina', '').strip()
        
        if not nome or not sobrenome:
            flash('Nome e sobrenome são obrigatórios!', 'danger')
            return redirect(url_for('formulario_identificacao'))
        
        session['nome'] = nome
        session['sobrenome'] = sobrenome
        session['instituicao'] = instituicao if instituicao else None
        session['disciplina'] = disciplina
        
        flash(f'Dados atualizados! Bem-vindo(a), {nome} {sobrenome}!', 'success')
        return redirect(url_for('formulario_identificacao'))
    
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
                         titulo='Formulário de Identificação')

# ============ ROTA LOGIN ============

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Rota Login"""
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if not usuario or not senha:
            flash('Usuário e senha são obrigatórios!', 'danger')
            return redirect(url_for('login'))
        
        if usuario == 'admin' and senha == '123456':
            session['usuario_logado'] = usuario
            flash(f'Login realizado com sucesso! Bem-vindo(a), {usuario}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
            return redirect(url_for('login'))
    
    return render_template('login.html',
                         current_time=datetime.utcnow(),
                         titulo='Login')

# ============ ROTA LOGOUT ============

@app.route('/logout')
def logout():
    """Rota Logout"""
    session.clear()
    flash('Logout realizado com sucesso!', 'info')
    return redirect(url_for('home'))

# ============ ROTA IDENTIFICAÇÃO ============

@app.route('/identificacao')
def identificacao():
    """Rota Identificação do Aluno"""
    return render_template('identificacao.html',
                         titulo='Identificação do Aluno')

# ============ ROTA CONTEXTO DA REQUISIÇÃO ============

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
                         titulo='Contexto da Requisição')

# ============ ROTA FORMULÁRIO SIMPLES ============

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    """Rota Formulário Simples"""
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
            if nome_atual:
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
                         titulo='Formulário Simples')

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
                         titulo=f'Usuário {name}')

# ============ CRIAÇÃO DO BANCO DE DADOS ============

# Cria as tabelas quando a aplicação inicia
with app.app_context():
    db.create_all()

# ============ EXECUÇÃO ============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
