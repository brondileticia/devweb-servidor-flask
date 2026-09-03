"""
Aplicação Flask - Avaliação Contínua: Semana 08
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Configuração SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# ============ MODELO USUARIO (COM FUNÇÃO) ============

class Usuario(db.Model):
    """
    Classe Usuario - Representa a tabela 'usuarios' no banco de dados
    Agora com campo 'funcao' (role)
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    funcao = db.Column(db.String(50), nullable=False, default='User')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, nome, funcao='User'):
        self.nome = nome
        self.funcao = funcao
    
    def __repr__(self):
        return f'<Usuario {self.nome} - {self.funcao}>'
    
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
    
    def promover(self):
        """Promove usuário para Administrator"""
        self.funcao = 'Administrator'
        db.session.commit()
    
    def rebaixar(self):
        """Rebaixa usuário para User"""
        self.funcao = 'User'
        db.session.commit()

# ============ DADOS DO ALUNO ============

ALUNO = {
    'nome': 'Leticia Brondi Carvalheiro',
    'prontuario': 'SEU_PRONTUARIO',
    'instituicao': 'IFSP',
    'curso': 'Análise e Desenvolvimento de Sistemas',
    'semestre': '4º Semestre',
    'campus': 'Pirituba'
}

DISCIPLINAS = ['DSWA5', 'DWBA4', 'Gestão de Projetos']

# ============ CONTEXT PROCESSOR ============

@app.context_processor
def inject_globals():
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliação contínua: Semana 08'
    }

# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

# ============ ROTA HOME ============

@app.route('/')
def home():
    """Home com cards"""
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
            'descricao': 'Usuários com funções e listagem',
            'url': '/banco-dados',
            'icone': 'glyphicon-hdd',
            'cor': 'panel-primary',
            'aula': 'Semana 08'
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

# ============ ROTA BANCO DE DADOS (ATUALIZADA - SEMANA 08) ============

@app.route('/banco-dados', methods=['GET', 'POST'])
def banco_dados():
    """
    Rota Banco de Dados - Usuários com funções
    """
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        funcao = request.form.get('funcao', 'User').strip()
        
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('banco_dados'))
        
        # Verifica se o usuário já existe
        usuario_existente = Usuario.query.filter_by(nome=nome).first()
        
        if usuario_existente:
            # Atualiza a função do usuário existente
            usuario_existente.funcao = funcao
            usuario_existente.atualizado_em = datetime.utcnow()
            db.session.commit()
            flash(f'Usuário "{nome}" já existe! Função atualizada para {funcao}!', 'warning')
        else:
            # Cria novo usuário
            novo_usuario = Usuario(nome, funcao)
            novo_usuario.salvar()
            flash(f'Usuário "{nome}" criado com função {funcao}!', 'success')
        
        return redirect(url_for('banco_dados'))
    
    # GET: Busca todos os usuários
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    ultimo_usuario = Usuario.query.order_by(Usuario.id.desc()).first()
    
    # Contagem
    total_usuarios = Usuario.query.count()
    total_admins = Usuario.query.filter_by(funcao='Administrator').count()
    total_users = Usuario.query.filter_by(funcao='User').count()
    
    return render_template('banco_dados.html',
                         usuarios=usuarios,
                         ultimo_usuario=ultimo_usuario,
                         total_usuarios=total_usuarios,
                         total_admins=total_admins,
                         total_users=total_users,
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados')

# ============ ROTA PARA DELETAR USUÁRIO ============

@app.route('/deletar-usuario/<int:usuario_id>')
def deletar_usuario(usuario_id):
    """Deleta um usuário específico"""
    usuario = Usuario.query.get_or_404(usuario_id)
    nome = usuario.nome
    usuario.deletar()
    flash(f'Usuário "{nome}" deletado com sucesso!', 'danger')
    return redirect(url_for('banco_dados'))

# ============ ROTA PARA PROMOVER USUÁRIO ============

@app.route('/promover-usuario/<int:usuario_id>')
def promover_usuario(usuario_id):
    """Promove usuário para Administrator"""
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.promover()
    flash(f'Usuário "{usuario.nome}" promovido para Administrator!', 'success')
    return redirect(url_for('banco_dados'))

# ============ ROTA PARA REBAIXAR USUÁRIO ============

@app.route('/rebaixar-usuario/<int:usuario_id>')
def rebaixar_usuario(usuario_id):
    """Rebaixa usuário para User"""
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario.rebaixar()
    flash(f'Usuário "{usuario.nome}" rebaixado para User!', 'warning')
    return redirect(url_for('banco_dados'))

# ============ DEMAIS ROTAS (MANTIDAS) ============

@app.route('/data-hora')
def data_hora():
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora')

@app.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    # Código existente...
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

# ============ CRIAÇÃO DO BANCO ============

with app.app_context():
    try:
        db.create_all()
        print("✅ Banco de dados criado com sucesso!")
        
        # Verificar se já existem usuários
        total = Usuario.query.count()
        print(f"📊 Total de usuários: {total}")
        
        if total == 0:
            # Criar usuários iniciais de exemplo
            usuarios_iniciais = [
                Usuario("Letícia Brondi", "Administrator"),
                Usuario("Fábio", "User"),
                Usuario("Taissa", "User")
            ]
            
            for u in usuarios_iniciais:
                u.salvar()
            
            print("✅ Usuários iniciais criados!")
    except Exception as e:
        print(f"❌ Erro: {e}")

# ============ EXECUÇÃO ============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
