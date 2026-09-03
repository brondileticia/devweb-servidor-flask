"""
Aplicação Flask - Avaliação Contínua: Semana 08
Disciplina: PTBDSWS - Programação em Desenvolvimento Web Servidor
Aluno: Leticia Brondi Carvalheiro
Instituição: IFSP - Campus Pirituba

Funcionalidades:
- Banco de dados SQLite com SQLAlchemy
- Modelo Usuario com funções (User/Administrator)
- CRUD completo de usuários
- Reset do banco via interface
- Listagem com estatísticas
- Promover/Rebaixar usuários
- Deletar usuários
"""

from datetime import datetime
from flask import (Flask, render_template, request, session, 
                   flash, redirect, url_for, abort, make_response, jsonify)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import flask
import os

# ============ CONFIGURAÇÃO DA APLICAÇÃO ============

app = Flask(__name__)

# Chave secreta para sessões
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Configuração do Banco de Dados SQLite
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# ============ MODELOS (CLASSES DE BANCO DE DADOS) ============

class Usuario(db.Model):
    """
    Classe Usuario - Representa a tabela 'usuarios' no banco de dados
    
    Atributos:
    - id: Identificador único
    - nome: Nome do usuário
    - funcao: Função do usuário (User ou Administrator)
    - criado_em: Data de criação
    - atualizado_em: Data da última atualização
    """
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    funcao = db.Column(db.String(50), nullable=False, default='User')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, nome, funcao='User'):
        self.nome = nome.strip()
        self.funcao = funcao.strip()
    
    def __repr__(self):
        return f'<Usuario {self.nome} - {self.funcao}>'
    
    def salvar(self):
        """Salva o usuário no banco de dados"""
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar: {e}")
            return False
    
    def atualizar(self, novo_nome=None, nova_funcao=None):
        """Atualiza o nome e/ou função do usuário"""
        try:
            if novo_nome:
                self.nome = novo_nome.strip()
            if nova_funcao:
                self.funcao = nova_funcao.strip()
            self.atualizado_em = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar: {e}")
            return False
    
    def deletar(self):
        """Remove o usuário do banco de dados"""
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao deletar: {e}")
            return False
    
    def promover(self):
        """Promove usuário para Administrator"""
        return self.atualizar(nova_funcao='Administrator')
    
    def rebaixar(self):
        """Rebaixa usuário para User"""
        return self.atualizar(nova_funcao='User')
    
    def to_dict(self):
        """Converte o objeto para dicionário (para API)"""
        return {
            'id': self.id,
            'nome': self.nome,
            'funcao': self.funcao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None,
            'atualizado_em': self.atualizado_em.isoformat() if self.atualizado_em else None
        }

# ============ DADOS DO ALUNO ============

ALUNO = {
    'nome': 'Leticia Brondi Carvalheiro',
    'prontuario': 'SEU_PRONTUARIO',
    'instituicao': 'IFSP',
    'curso': 'Análise e Desenvolvimento de Sistemas',
    'semestre': '4º Semestre',
    'campus': 'Pirituba'
}

# Lista de disciplinas disponíveis
DISCIPLINAS = ['DSWA5', 'DWBA4', 'Gestão de Projetos']

# Funções disponíveis
FUNCOES = ['User', 'Administrator']

# ============ FUNÇÕES AUXILIARES ============

def criar_usuarios_iniciais():
    """
    Cria usuários iniciais no banco de dados
    """
    usuarios_iniciais = [
        Usuario("john", "Administrator"),
        Usuario("susan", "User"),
        Usuario("david", "User"),
        Usuario("Professor Fabio Teixeira", "User")
    ]
    
    for usuario in usuarios_iniciais:
        usuario.salvar()
    
    return len(usuarios_iniciais)

def resetar_banco_dados():
    """
    Reseta o banco de dados completamente
    Remove todas as tabelas e recria com dados iniciais
    """
    try:
        # Remove todas as tabelas
        db.drop_all()
        
        # Recria as tabelas
        db.create_all()
        
        # Cria usuários iniciais
        total = criar_usuarios_iniciais()
        
        return True, f"Banco resetado com sucesso! {total} usuários iniciais criados."
    except Exception as e:
        db.session.rollback()
        return False, f"Erro ao resetar banco: {e}"

def get_estatisticas():
    """
    Retorna estatísticas do banco de dados
    """
    total_usuarios = Usuario.query.count()
    total_admins = Usuario.query.filter_by(funcao='Administrator').count()
    total_users = Usuario.query.filter_by(funcao='User').count()
    
    return {
        'total_usuarios': total_usuarios,
        'total_admins': total_admins,
        'total_users': total_users
    }

# ============ CONTEXT PROCESSOR ============

@app.context_processor
def inject_globals():
    """Injeta variáveis globais em todos os templates"""
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliação contínua: Semana 08',
        'funcoes': FUNCOES
    }

# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('404.html', 
                         titulo='Acesso negado',
                         mensagem='Você não tem permissão para acessar esta página.'), 403

# ============ ROTA HOME ============

@app.route('/')
def home():
    """Rota Home - Página principal com cards de navegação"""
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
                         titulo='Home',
                         descricao='Página central com todas as atividades')

# ============ ROTA BANCO DE DADOS ============

@app.route('/banco-dados', methods=['GET', 'POST'])
def banco_dados():
    """
    Rota Banco de Dados - CRUD de usuários
    """
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        funcao = request.form.get('funcao', 'User').strip()
        
        # Validações
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('banco_dados'))
        
        if len(nome) > 100:
            flash('Nome muito longo! Máximo de 100 caracteres.', 'danger')
            return redirect(url_for('banco_dados'))
        
        if funcao not in FUNCOES:
            funcao = 'User'
        
        # Verifica se o usuário já existe (case insensitive)
        usuario_existente = Usuario.query.filter(
            db.func.lower(Usuario.nome) == db.func.lower(nome)
        ).first()
        
        if usuario_existente:
            # Atualiza a função do usuário existente
            usuario_existente.atualizar(nova_funcao=funcao)
            flash(f'Usuário "{nome}" já existe! Função atualizada para {funcao}!', 'warning')
        else:
            # Cria novo usuário
            novo_usuario = Usuario(nome, funcao)
            if novo_usuario.salvar():
                flash(f'Usuário "{nome}" criado com função {funcao}!', 'success')
            else:
                flash(f'Erro ao criar usuário "{nome}"!', 'danger')
        
        return redirect(url_for('banco_dados'))
    
    # GET: Busca dados
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    ultimo_usuario = Usuario.query.order_by(Usuario.id.desc()).first()
    stats = get_estatisticas()
    
    return render_template('banco_dados.html',
                         usuarios=usuarios,
                         ultimo_usuario=ultimo_usuario,
                         **stats,
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados',
                         descricao='Usuários com funções e persistência')

# ============ ROTA PARA RESETAR O BANCO ============

@app.route('/resetar-banco')
def resetar_banco():
    """Rota para resetar o banco de dados"""
    sucesso, mensagem = resetar_banco_dados()
    
    if sucesso:
        flash(mensagem, 'success')
    else:
        flash(mensagem, 'danger')
    
    return redirect(url_for('banco_dados'))

# ============ ROTA PARA DELETAR USUÁRIO ============

@app.route('/deletar-usuario/<int:usuario_id>')
def deletar_usuario(usuario_id):
    """Deleta um usuário específico"""
    usuario = Usuario.query.get_or_404(usuario_id)
    nome = usuario.nome
    
    if usuario.deletar():
        flash(f'Usuário "{nome}" deletado com sucesso!', 'danger')
    else:
        flash(f'Erro ao deletar usuário "{nome}"!', 'danger')
    
    return redirect(url_for('banco_dados'))

# ============ ROTA PARA PROMOVER USUÁRIO ============

@app.route('/promover-usuario/<int:usuario_id>')
def promover_usuario(usuario_id):
    """Promove usuário para Administrator"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.promover():
        flash(f'Usuário "{usuario.nome}" promovido para Administrator!', 'success')
    else:
        flash(f'Erro ao promover usuário "{usuario.nome}"!', 'danger')
    
    return redirect(url_for('banco_dados'))

# ============ ROTA PARA REBAIXAR USUÁRIO ============

@app.route('/rebaixar-usuario/<int:usuario_id>')
def rebaixar_usuario(usuario_id):
    """Rebaixa usuário para User"""
    usuario = Usuario.query.get_or_404(usuario_id)
    
    if usuario.rebaixar():
        flash(f'Usuário "{usuario.nome}" rebaixado para User!', 'warning')
    else:
        flash(f'Erro ao rebaixar usuário "{usuario.nome}"!', 'danger')
    
    return redirect(url_for('banco_dados'))

# ============ API JSON ============

@app.route('/api/usuarios')
def api_usuarios():
    """API - Retorna todos os usuários em JSON"""
    usuarios = Usuario.query.all()
    return jsonify([u.to_dict() for u in usuarios])

@app.route('/api/usuarios/<int:usuario_id>')
def api_usuario(usuario_id):
    """API - Retorna um usuário específico em JSON"""
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify(usuario.to_dict())

# ============ ROTA DATA E HORA ============

@app.route('/data-hora')
def data_hora():
    """Rota Data e Hora"""
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora')

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
        
        # Simulação de autenticação (substituir por banco de dados real)
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
    method = request.method
    path = request.path
    
    return render_template('contextorequisicao.html',
                         user_agent=user_agent,
                         remote_ip=remote_ip,
                         host=host,
                         method=method,
                         path=path,
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

# ============ CRIAÇÃO DO BANCO ============

with app.app_context():
    try:
        db.create_all()
        print("✅ Banco de dados criado/verificado com sucesso!")
        
        # Verifica se já existem usuários
        total = Usuario.query.count()
        print(f"📊 Total de usuários: {total}")
        
        if total == 0:
            # Cria usuários iniciais
            criar_usuarios_iniciais()
            print("✅ Usuários iniciais criados!")
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")

# ============ EXECUÇÃO ============

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
