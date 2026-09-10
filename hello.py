"""
Aplicação Flask - Avaliação Contínua: Semana 09
Disciplina: PTBDSWS - Programação em Desenvolvimento Web Servidor
Aluno: Leticia Brondi Carvalheiro
Instituição: IFSP - Campus Pirituba

Funcionalidades:
- Banco de dados SQLite com SQLAlchemy
- Modelo Usuario com 3 funções: User, Moderator, Administrator
- CRUD completo de usuários
- Listagem de usuários agrupados por função
- Contador de usuários e de funções
- Estatísticas por função
- Promover/Rebaixar com ciclo de 3 níveis
"""

from datetime import datetime
from flask import (Flask, render_template, request, session, 
                   flash, redirect, url_for, abort, jsonify)
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import flask
import os

# ============ CONFIGURAÇÃO ============

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

# ============ MODELO ============

class Usuario(db.Model):
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
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar: {e}")
            return False
    
    def atualizar(self, novo_nome=None, nova_funcao=None):
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
            return False
    
    def deletar(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def promover(self):
        """Promove: User → Moderator → Administrator"""
        ciclo = {'User': 'Moderator', 'Moderator': 'Administrator', 'Administrator': 'Administrator'}
        self.funcao = ciclo.get(self.funcao, 'User')
        db.session.commit()
        return True
    
    def rebaixar(self):
        """Rebaixa: Administrator → Moderator → User"""
        ciclo = {'Administrator': 'Moderator', 'Moderator': 'User', 'User': 'User'}
        self.funcao = ciclo.get(self.funcao, 'User')
        db.session.commit()
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'funcao': self.funcao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }

# ============ DADOS ============

ALUNO = {
    'nome': 'Leticia Brondi Carvalheiro',
    'prontuario': 'SEU_PRONTUARIO',
    'instituicao': 'IFSP'
}

DISCIPLINAS = ['DSWA5', 'DWBA4', 'Gestão de Projetos']

# ⭐ NOVA LISTA COM MODERATOR
FUNCOES = ['User', 'Moderator', 'Administrator']

# Hierarquia (para ordenação e exibição)
HIERARQUIA_FUNCOES = {
    'Administrator': 1,
    'Moderator': 2,
    'User': 3
}

# Ícones e cores para cada função
ICONES_FUNCOES = {
    'Administrator': {'icone': 'glyphicon-king', 'cor': 'danger', 'label': 'label-danger'},
    'Moderator': {'icone': 'glyphicon-eye-open', 'cor': 'warning', 'label': 'label-warning'},
    'User': {'icone': 'glyphicon-user', 'cor': 'info', 'label': 'label-info'}
}

# ============ FUNÇÕES AUXILIARES ============

def criar_usuarios_iniciais():
    """Cria usuários iniciais (um de cada função)"""
    usuarios = [
        Usuario("john", "Administrator"),
        Usuario("susan", "User"),
        Usuario("david", "User"),
        Usuario("Professor Fabio Teixeira", "User")
    ]
    for u in usuarios:
        db.session.add(u)
    db.session.commit()
    return len(usuarios)

def get_estatisticas():
    """Retorna estatísticas completas"""
    total_usuarios = Usuario.query.count()
    
    # Contador por função
    contagem_por_funcao = {}
    for funcao in FUNCOES:
        contagem_por_funcao[funcao] = Usuario.query.filter_by(funcao=funcao).count()
    
    # ⭐ CONTADOR DE FUNÇÕES (quantas funções têm pelo menos 1 usuário)
    funcoes_em_uso = sum(1 for qtd in contagem_por_funcao.values() if qtd > 0)
    total_funcoes = len(FUNCOES)  # Total de funções disponíveis
    
    return {
        'total_usuarios': total_usuarios,
        'total_funcoes': total_funcoes,
        'funcoes_em_uso': funcoes_em_uso,
        'contagem_por_funcao': contagem_por_funcao,
        'total_admins': contagem_por_funcao.get('Administrator', 0),
        'total_moderators': contagem_por_funcao.get('Moderator', 0),
        'total_users': contagem_por_funcao.get('User', 0)
    }

def get_usuarios_por_funcao():
    """
    ⭐ Retorna usuários agrupados por função
    Formato: {'Administrator': [...], 'Moderator': [...], 'User': [...]}
    """
    agrupado = {}
    for funcao in FUNCOES:  # Mantém a ordem definida
        usuarios = Usuario.query.filter_by(funcao=funcao).order_by(Usuario.nome).all()
        if usuarios:  # Só inclui se tiver usuários
            agrupado[funcao] = usuarios
    return agrupado

# ============ CONTEXT PROCESSOR ============

@app.context_processor
def inject_globals():
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliação contínua: Semana 09',
        'funcoes': FUNCOES,
        'icones_funcoes': ICONES_FUNCOES,
        'hierarquia_funcoes': HIERARQUIA_FUNCOES
    }

# ============ ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', titulo='Erro do servidor'), 500

# ============ HOME ============

@app.route('/')
def home():
    paginas = [
        {'titulo': 'Data e Hora', 'descricao': 'Data, hora e informações temporais',
         'url': '/data-hora', 'icone': 'glyphicon-time', 'cor': 'panel-primary', 'aula': 'Aula 040'},
        {'titulo': 'Identificação do Aluno', 'descricao': 'Dados do aluno',
         'url': '/identificacao', 'icone': 'glyphicon-user', 'cor': 'panel-success', 'aula': 'Aula 040'},
        {'titulo': 'Contexto da Requisição', 'descricao': 'Dados técnicos HTTP',
         'url': '/contextorequisicao', 'icone': 'glyphicon-info-sign', 'cor': 'panel-info', 'aula': 'Aula 040'},
        {'titulo': 'Formulário de Identificação', 'descricao': 'Nome e disciplina',
         'url': '/formulario-identificacao', 'icone': 'glyphicon-edit', 'cor': 'panel-warning', 'aula': 'Aula 050.B'},
        {'titulo': 'Login', 'descricao': 'Sistema de autenticação',
         'url': '/login', 'icone': 'glyphicon-log-in', 'cor': 'panel-danger', 'aula': 'Aula 050.B'},
        {'titulo': 'Banco de Dados', 'descricao': 'Usuários agrupados por função',
         'url': '/banco-dados', 'icone': 'glyphicon-hdd', 'cor': 'panel-primary', 'aula': 'Semana 09'},
        {'titulo': 'Formulário Simples', 'descricao': 'Formulário básico',
         'url': '/formulario', 'icone': 'glyphicon-pencil', 'cor': 'panel-default', 'aula': 'Extra'}
    ]
    return render_template('home.html', paginas=paginas,
                         current_time=datetime.utcnow(), titulo='Home')

# ============ BANCO DE DADOS (SEMANA 09) ============

@app.route('/banco-dados', methods=['GET', 'POST'])
def banco_dados():
    """Rota Banco de Dados - CRUD + agrupamento"""
    
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        funcao = request.form.get('funcao', 'User').strip()
        
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('banco_dados'))
        
        if funcao not in FUNCOES:
            funcao = 'User'
        
        # Verifica duplicata
        existente = Usuario.query.filter(
            db.func.lower(Usuario.nome) == db.func.lower(nome)
        ).first()
        
        if existente:
            existente.funcao = funcao
            existente.atualizado_em = datetime.utcnow()
            db.session.commit()
            flash(f'Usuário "{nome}" já existe! Função atualizada para {funcao}!', 'warning')
        else:
            novo = Usuario(nome, funcao)
            db.session.add(novo)
            db.session.commit()
            flash(f'Usuário "{nome}" criado como {funcao}!', 'success')
        
        return redirect(url_for('banco_dados'))
    
    # GET - Buscar dados
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    usuarios_por_funcao = get_usuarios_por_funcao()  # ⭐ NOVO
    stats = get_estatisticas()
    
    return render_template('banco_dados.html',
                         usuarios=usuarios,
                         usuarios_por_funcao=usuarios_por_funcao,  # ⭐ NOVO
                         **stats,
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados')

# ============ AÇÕES ============

@app.route('/deletar-usuario/<int:usuario_id>')
def deletar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        nome = usuario.nome
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário "{nome}" deletado!', 'danger')
    return redirect(url_for('banco_dados'))

@app.route('/promover-usuario/<int:usuario_id>')
def promover_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        antiga = usuario.funcao
        usuario.promover()
        flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'success')
    return redirect(url_for('banco_dados'))

@app.route('/rebaixar-usuario/<int:usuario_id>')
def rebaixar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        antiga = usuario.funcao
        usuario.rebaixar()
        flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'warning')
    return redirect(url_for('banco_dados'))

@app.route('/resetar-banco')
def resetar_banco():
    try:
        Usuario.query.delete()
        db.session.commit()
        criar_usuarios_iniciais()
        flash('Banco resetado com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro: {e}', 'danger')
    return redirect(url_for('banco_dados'))

# ============ API ============

@app.route('/api/usuarios')
def api_usuarios():
    return jsonify([u.to_dict() for u in Usuario.query.all()])

@app.route('/api/usuarios-por-funcao')
def api_usuarios_por_funcao():
    """API que retorna usuários agrupados"""
    resultado = {}
    for funcao, usuarios in get_usuarios_por_funcao().items():
        resultado[funcao] = [u.to_dict() for u in usuarios]
    return jsonify(resultado)

@app.route('/api/estatisticas')
def api_estatisticas():
    """API com estatísticas completas"""
    return jsonify(get_estatisticas())

# ============ DEMAIS ROTAS ============

@app.route('/data-hora')
def data_hora():
    return render_template('data_hora.html', current_time=datetime.utcnow(), titulo='Data e Hora')

@app.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    nome = session.get('nome', '')
    sobrenome = session.get('sobrenome', '')
    instituicao = session.get('instituicao', None)
    disciplina = session.get('disciplina', '')
    
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
                         nome=nome, sobrenome=sobrenome,
                         nome_completo=nome_completo,
                         instituicao=instituicao, disciplina=disciplina,
                         disciplinas=DISCIPLINAS,
                         current_time=datetime.utcnow(),
                         titulo='Formulário de Identificação')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if usuario == 'admin' and senha == '123456':
            session['usuario_logado'] = usuario
            flash(f'Login realizado! Bem-vindo(a), {usuario}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('login.html', current_time=datetime.utcnow(), titulo='Login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado!', 'info')
    return redirect(url_for('home'))

@app.route('/identificacao')
def identificacao():
    return render_template('identificacao.html', titulo='Identificação do Aluno')

@app.route('/contextorequisicao')
def contextorequisicao():
    return render_template('contextorequisicao.html',
                         user_agent=request.headers.get('User-Agent', 'Desconhecido'),
                         remote_ip=request.remote_addr or 'Desconhecido',
                         host=request.host or 'Desconhecido',
                         titulo='Contexto da Requisição')

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    nome_atual = session.get('nome_usuario', None)
    
    if request.method == 'POST':
        novo_nome = request.form.get('nome', '').strip()
        if novo_nome:
            if nome_atual and nome_atual != novo_nome:
                flash(f'"{nome_atual}" → "{novo_nome}"', 'warning')
            else:
                flash(f'Bem-vindo(a), {novo_nome}!', 'success')
            session['nome_usuario'] = novo_nome
        else:
            session.pop('nome_usuario', None)
        return redirect(url_for('formulario'))
    
    nome_atual = session.get('nome_usuario', None)
    return render_template('formulario.html', nome=nome_atual, titulo='Formulário Simples')

@app.route('/user/<name>')
def user(name):
    name = name.replace('<', '').replace('>', '').strip()
    return render_template('user.html', name=name, titulo=f'Usuário {name}')

# ============ CRIAÇÃO DO BANCO ============

with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas/verificadas!")
    try:
        total = Usuario.query.count()
        print(f"📊 Total de usuários: {total}")
        if total == 0:
            criar_usuarios_iniciais()
            print("✅ Usuários iniciais criados!")
    except Exception as e:
        print(f"⚠️ Erro: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
