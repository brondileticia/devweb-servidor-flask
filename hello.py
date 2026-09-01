"""
Aplicação Flask - Avaliação Contínua: Semana 07
Disciplina: PTBDSWS
"""

from datetime import datetime
from flask import (Flask, render_template, request, session, 
                   flash, redirect, url_for, abort, make_response)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import flask
import os

# ============ CONFIGURAÇÃO ============
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Configuração SQLite (CORRIGIDA)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# ============ MODELO ============
class Usuario(db.Model):
    """Classe Usuario - Tabela usuarios no banco"""
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
        db.session.add(self)
        db.session.commit()
    
    def atualizar(self, novo_nome):
        self.nome = novo_nome
        self.atualizado_em = datetime.utcnow()
        db.session.commit()
    
    def deletar(self):
        db.session.delete(self)
        db.session.commit()

# ============ DADOS ============
ALUNO = {
    'nome': 'Leticia Brondi',
    'prontuario': 'SEU_PRONTUARIO',
    'instituicao': 'IFSP'
}

DISCIPLINAS = ['DSWA5', 'DWBA4', 'Gestão de Projetos']

# ============ CONTEXT PROCESSOR ============
@app.context_processor
def inject_globals():
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliação contínua: Semana 07'
    }

# ============ ERROS ============
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

# ============ ROTA HOME ============
@app.route('/')
def home():
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
            'descricao': 'Dados de identificação do aluno',
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
            'descricao': 'Formulário com nome e disciplina',
            'url': '/formulario-identificacao',
            'icone': 'glyphicon-edit',
            'cor': 'panel-warning',
            'aula': 'Aula 050.B'
        },
        {
            'titulo': 'Login',
            'descricao': 'Sistema de autenticação',
            'url': '/login',
            'icone': 'glyphicon-log-in',
            'cor': 'panel-danger',
            'aula': 'Aula 050.B'
        },
        {
            'titulo': 'Banco de Dados',
            'descricao': 'Usuários com SQLite',
            'url': '/banco-dados',
            'icone': 'glyphicon-hdd',
            'cor': 'panel-primary',
            'aula': 'Semana 07'
        },
        {
            'titulo': 'Formulário Simples',
            'descricao': 'Formulário básico com sessão',
            'url': '/formulario',
            'icone': 'glyphicon-pencil',
            'cor': 'panel-default',
            'aula': 'Extra'
        }
    ]
    
    return render_template('home.html',
                         paginas=paginas,
                         current_time=datetime.utcnow(),
                         titulo='Home')

# ============ ROTA BANCO DE DADOS ============
@app.route('/banco-dados', methods=['GET', 'POST'])
def banco_dados():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('banco_dados'))
        
        # Verifica se existe usuário
        usuario_existente = Usuario.query.first()
        
        if usuario_existente:
            usuario_existente.atualizar(nome)
            flash(f'Nome atualizado para "{nome}"!', 'success')
        else:
            novo_usuario = Usuario(nome)
            novo_usuario.salvar()
            flash(f'Usuário "{nome}" criado!', 'success')
        
        return redirect(url_for('banco_dados'))
    
    # GET
    usuario = Usuario.query.order_by(Usuario.id.desc()).first()
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    
    return render_template('banco_dados.html',
                         usuario=usuario,
                         usuarios=usuarios,
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados')

# ============ OUTRAS ROTAS (SIMPLIFICADAS) ============
@app.route('/data-hora')
def data_hora():
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora')

@app.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    return render_template('formulario_identificacao.html',
                         current_time=datetime.utcnow(),
                         titulo='Formulário de Identificação')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html',
                         current_time=datetime.utcnow(),
                         titulo='Login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado!', 'info')
    return redirect(url_for('home'))

@app.route('/identificacao')
def identificacao():
    return render_template('identificacao.html',
                         titulo='Identificação do Aluno')

@app.route('/contextorequisicao')
def contextorequisicao():
    return render_template('contextorequisicao.html',
                         titulo='Contexto da Requisição')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    return render_template('formulario.html',
                         titulo='Formulário Simples')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',
                         name=name,
                         titulo=f'Usuário {name}')

# ============ CRIAÇÃO DO BANCO (AGORA COM VERIFICAÇÃO) ============
with app.app_context():
    try:
        db.create_all()
        print("✅ Banco de dados criado com sucesso!")
        
        # Verificar se o arquivo existe
        if os.path.exists(os.path.join(BASE_DIR, 'app.db')):
            print("✅ Arquivo app.db criado em:", os.path.join(BASE_DIR, 'app.db'))
        else:
            print("⚠️ Arquivo app.db não encontrado")
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")

# ============ EXECUÇÃO ============
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
