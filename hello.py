from datetime import datetime
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
import flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'chave-secreta-para-sessoes'  # Necessário para session e flash

bootstrap = Bootstrap(app)
moment = Moment(app)

# Configurações do aluno
ALUNO = {
    'nome': 'Fabio Teixeira',
    'prontuario': 'PT23820X',
    'instituicao': 'IFSP'
}

# Context processor para injetar variáveis globais
@app.context_processor
def inject_globals():
    return {
        'flask_version': flask.__version__,
        'aluno': ALUNO
    }

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/')
def index():
    """Rota Home - mostra data/hora atual"""
    return render_template('index.html', 
                         current_time=datetime.utcnow(),
                         titulo='Home')

@app.route('/identificacao')
def identificacao():
    """Rota Identificação - dados do aluno"""
    return render_template('identificacao.html',
                         titulo='Identificação')

@app.route('/contextorequisicao')
def contextorequisicao():
    """Rota Contexto da Requisição - dados do navegador e servidor"""
    user_agent = request.headers.get('User-Agent', 'Desconhecido')
    remote_ip = request.remote_addr
    host = request.host
    
    return render_template('contextorequisicao.html',
                         user_agent=user_agent,
                         remote_ip=remote_ip,
                         host=host,
                         titulo='Contexto da requisição')

# ============ NOVA ROTA PARA O FORMULÁRIO ============
@app.route('/formulario', methods=['GET', 'POST'])
def formulario():
    """
    Rota que recebe um nome via formulário.
    - GET: Mostra o formulário
    - POST: Processa o nome enviado
    """
    nome_atual = None
    nome_anterior = None
    nome_mudou = False
    
    if request.method == 'POST':
        # Pega o nome enviado pelo formulário
        novo_nome = request.form.get('nome', '').strip()
        
        # Verifica se já existe um nome na sessão
        if 'nome_usuario' in session:
            nome_anterior = session['nome_usuario']
            
            # Verifica se o nome mudou
            if nome_anterior != novo_nome and novo_nome != '':
                nome_mudou = True
                flash(f'O nome foi alterado de "{nome_anterior}" para "{novo_nome}"!', 'warning')
        
        # Atualiza a sessão com o novo nome
        if novo_nome != '':
            session['nome_usuario'] = novo_nome
            nome_atual = novo_nome
        else:
            # Se o campo estiver vazio, remove da sessão
            session.pop('nome_usuario', None)
            nome_atual = None
        
        # Redireciona para evitar reenvio do formulário (PRG pattern)
        return redirect(url_for('formulario'))
    
    else:
        # GET: Pega o nome da sessão (se existir)
        nome_atual = session.get('nome_usuario', None)
    
    return render_template('formulario.html',
                         nome=nome_atual,
                         nome_mudou=nome_mudou,
                         titulo='Formulário')

@app.route('/user/<name>')
def user(name):
    """Rota dinâmica de usuário"""
    return render_template('user.html', 
                         name=name,
                         titulo=f'Usuário {name}')

if __name__ == '__main__':
    app.run(debug=True)
