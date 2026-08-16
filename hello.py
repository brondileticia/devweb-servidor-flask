"""
Aplicação Flask - Avaliação Contínua: Aula 040
Disciplina: PTBDSWS - Programação em Desenvolvimento Web Servidor
Aluno: Leticia Brondi
Instituição: IFSP - Campus Pirituba

Esta aplicação demonstra:
- Rotas básicas e dinâmicas
- Templates com Jinja2 e Bootstrap
- Sessões de usuário
- Flash messages
- Contexto da requisição HTTP
- Formulários com método POST
- Integração com Moment.js para datas
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

# Chave secreta para sessões e flash messages
# Em produção, use uma chave forte e não exponha no código
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-desenvolvimento')

# Configurações adicionais
app.config['JSON_SORT_KEYS'] = False  # Mantém ordem dos dicionários em JSON
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads

# Inicialização das extensões
bootstrap = Bootstrap(app)
moment = Moment(app)

# ============ DADOS DO ALUNO ============

ALUNO = {
    'nome': 'Leticia Brondi',
    'prontuario': 'SEU_PRONTUARIO',  # Atualize com seu prontuário
    'instituicao': 'IFSP',
    'curso': 'Análise e Desenvolvimento de Sistemas',
    'semestre': '4º Semestre',
    'campus': 'Pirituba'
}

# ============ CONTEXT PROCESSOR ============

@app.context_processor
def inject_globals():
    """
    Injeta variáveis globais em todos os templates.
    Estas variáveis estarão disponíveis sem precisar passar em cada render_template.
    """
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO,
        'ano_atual': datetime.now().year,
        'app_name': 'Avaliação contínua: Aula 040'
    }

# ============ TRATAMENTO DE ERROS ============

@app.errorhandler(404)
def page_not_found(e):
    """Página personalizada para erro 404"""
    return render_template('404.html', titulo='Página não encontrada'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Página personalizada para erro 500"""
    return render_template('500.html', titulo='Erro do servidor'), 500

@app.errorhandler(403)
def forbidden(e):
    """Página personalizada para erro 403"""
    return render_template('404.html', 
                         titulo='Acesso negado',
                         mensagem='Você não tem permissão para acessar esta página.'), 403

# ============ ROTAS PRINCIPAIS ============

@app.route('/')
def index():
    """
    Rota Home - Página principal
    Mostra data e hora atual usando Moment.js
    """
    return render_template('index.html', 
                         current_time=datetime.utcnow(),
                         titulo='Home',
                         descricao='Página principal com data e hora atual')


@app.route('/identificacao')
def identificacao():
    """
    Rota Identificação - Mostra dados do aluno
    """
    return render_template('identificacao.html',
                         titulo='Identificação',
                         descricao='Dados de identificação do aluno')


@app.route('/contextorequisicao')
def contextorequisicao():
    """
    Rota Contexto da Requisição - Mostra dados técnicos da requisição HTTP
    """
    # Coleta dados da requisição
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    remote_ip = request.remote_addr or 'Desconhecido'
    host = request.host or 'Desconhecido'
    method = request.method
    path = request.path
    scheme = request.scheme
    
    # Informações adicionais
    headers = dict(request.headers)
    cookies = request.cookies
    
    return render_template('contextorequisicao.html',
                         user_agent=user_agent,
                         remote_ip=remote_ip,
                         host=host,
                         method=method,
                         path=path,
                         scheme=scheme,
                         headers=headers,
                         cookies=cookies,
                         titulo='Contexto da requisição',
                         descricao='Dados técnicos da requisição HTTP')


# ============ ROTA DO FORMULÁRIO ============

@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    """
    Rota do Formulário - Recebe e exibe nome do usuário
    
    Funcionalidades:
    - GET: Mostra formulário vazio ou com nome atual
    - POST: Processa nome enviado
    - Detecta mudança de nome
    - Mantém histórico na sessão
    - Usa PRG (Post/Redirect/Get) para evitar reenvio
    """
    nome_atual = session.get('nome_usuario', None)
    nome_anterior = session.get('nome_anterior', None)
    nome_mudou = False
    
    # Processamento do POST
    if request.method == 'POST':
        novo_nome = request.form.get('nome', '').strip()
        
        # Validação básica
        if len(novo_nome) > 100:
            flash('Nome muito longo! Máximo de 100 caracteres.', 'danger')
            return redirect(url_for('formulario'))
        
        # Remove caracteres perigosos (básico)
        novo_nome = novo_nome.replace('<', '').replace('>', '')
        
        # Se o campo não está vazio
        if novo_nome:
            # Verifica se já existia nome
            if nome_atual:
                # Detecta mudança de nome
                if nome_atual != novo_nome:
                    nome_mudou = True
                    session['nome_anterior'] = nome_atual
                    
                    # Flash message informando a mudança
                    flash(f'O nome foi alterado de "{nome_atual}" para "{novo_nome}"!', 'warning')
                    
                    # Adiciona ao histórico
                    _adicionar_ao_historico(novo_nome)
            else:
                # Primeiro nome
                flash(f'Bem-vindo(a), {novo_nome}!', 'success')
                _adicionar_ao_historico(novo_nome)
            
            # Atualiza a sessão
            session['nome_usuario'] = novo_nome
            
        else:
            # Campo vazio - remove nome
            if nome_atual:
                flash(f'Nome "{nome_atual}" removido!', 'info')
                session.pop('nome_usuario', None)
                session.pop('nome_anterior', None)
        
        # PRG Pattern: Redireciona para GET
        return redirect(url_for('formulario'))
    
    # GET: Verifica se é para limpar
    if request.args.get('limpar') == 'true':
        _limpar_sessao()
        return redirect(url_for('formulario'))
    
    # GET: Busca dados da sessão
    nome_atual = session.get('nome_usuario', None)
    historico = session.get('historico_nomes', [])
    
    return render_template('formulario.html',
                         nome=nome_atual,
                         nome_mudou=nome_mudou,
                         historico=historico,
                         titulo='Formulário',
                         descricao='Formulário interativo com sessão')


def _adicionar_ao_historico(nome):
    """
    Função auxiliar para adicionar nome ao histórico da sessão
    Mantém máximo de 10 nomes no histórico
    """
    if 'historico_nomes' not in session:
        session['historico_nomes'] = []
    
    historico = session['historico_nomes']
    
    # Evita duplicatas consecutivas
    if not historico or historico[-1] != nome:
        historico.append(nome)
    
    # Limita a 10 itens
    if len(historico) > 10:
        historico = historico[-10:]
    
    session['historico_nomes'] = historico


def _limpar_sessao():
    """
    Função auxiliar para limpar dados da sessão
    """
    session.pop('nome_usuario', None)
    session.pop('nome_anterior', None)
    session.pop('historico_nomes', None)
    flash('Sessão limpa com sucesso!', 'info')


# ============ ROTA DINÂMICA DE USUÁRIO ============

@app.route('/user/<name>')
def user(name):
    """
    Rota dinâmica - Exibe página personalizada para um nome
    
    Parâmetros:
    - name: Nome passado na URL
    
    Exemplo: /user/Leticia mostra "Hello, Leticia!"
    """
    # Sanitiza o nome (remove caracteres perigosos)
    name = name.replace('<', '').replace('>', '').strip()
    
    if not name:
        flash('Nome inválido!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('user.html',
                         name=name,
                         titulo=f'Usuário {name}',
                         descricao=f'Página personalizada para {name}')


# ============ ROTAS ADICIONAIS (EXEMPLOS) ============

@app.route('/sobre')
def sobre():
    """
    Rota Sobre - Informações sobre a aplicação
    """
    tecnologias = [
        {'nome': 'Flask', 'versao': flask.__version__, 'url': 'https://flask.palletsprojects.com/'},
        {'nome': 'Bootstrap', 'versao': '3.4.1', 'url': 'https://getbootstrap.com/docs/3.3/'},
        {'nome': 'Moment.js', 'versao': '2.29.1', 'url': 'https://momentjs.com/'},
        {'nome': 'Python', 'versao': '3.10', 'url': 'https://www.python.org/'}
    ]
    
    return render_template('sobre.html',
                         tecnologias=tecnologias,
                         titulo='Sobre',
                         descricao='Informações sobre a aplicação e tecnologias')


@app.route('/saudacao')
@app.route('/saudacao/<nome>')
def saudacao(nome=None):
    """
    Rota com parâmetro opcional
    - /saudacao -> "Olá, visitante!"
    - /saudacao/Leticia -> "Olá, Leticia!"
    """
    if nome:
        return f'<h1>Olá, {nome}!</h1>'
    return '<h1>Olá, visitante!</h1>'


# ============ ROTAS DE DEMONSTRAÇÃO (ATIVIDADE 1) ============

@app.route('/codigostatusdiferente')
def codigostatusdiferente():
    """Demonstra resposta com código de status diferente"""
    return '<p>Bad request</p>', 400


@app.route('/objetoresposta')
def objetoresposta():
    """Demonstra criação de resposta com cookie"""
    response = make_response('<h1>This document carries a cookie!</h1>')
    response.set_cookie('answer', '42')
    return response


@app.route('/redirecionamento')
def redirecionamento():
    """Demonstra redirecionamento"""
    return redirect('https://ptb.ifsp.edu.br/')


@app.route('/abortar')
def abortar():
    """Demonstra abort com erro 404"""
    abort(404)


# ============ API JSON (EXEMPLO) ============

@app.route('/api/aluno')
def api_aluno():
    """
    Rota API - Retorna dados do aluno em JSON
    Exemplo de como criar uma API RESTful
    """
    from flask import jsonify
    
    dados = {
        'nome': ALUNO['nome'],
        'prontuario': ALUNO['prontuario'],
        'instituicao': ALUNO['instituicao'],
        'curso': ALUNO['curso'],
        'semestre': ALUNO['semestre']
    }
    
    return jsonify(dados)


@app.route('/api/hora')
def api_hora():
    """
    Rota API - Retorna hora atual em JSON
    """
    from flask import jsonify
    
    return jsonify({
        'hora_utc': datetime.utcnow().isoformat(),
        'timestamp': int(datetime.utcnow().timestamp())
    })


# ============ EXECUÇÃO ============

if __name__ == '__main__':
    # Executa a aplicação em modo debug (apenas desenvolvimento)
    # Em produção (PythonAnywhere), o servidor WSGI ignora este bloco
    app.run(
        debug=True,          # Ativa modo debug
        host='0.0.0.0',     # Acessível de qualquer IP
        port=5000           # Porta padrão do Flask
    )
