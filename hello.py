from datetime import datetime
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_moment import Moment

app = Flask(__name__)

bootstrap = Bootstrap(app)
moment = Moment(app)

# Configurações do aluno
ALUNO = {
    'nome': 'Letícia Brondi',
    'prontuario': 'PT3037801',
    'instituicao': 'IFSP'
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
                         aluno=ALUNO,
                         titulo='Identificação')

@app.route('/contextorequisicao')
def contextorequisicao():
    """Rota Contexto da Requisição - dados do navegador e servidor"""
    user_agent = request.headers.get('User-Agent')
    remote_ip = request.remote_addr
    host = request.host
    
    return render_template('contextorequisicao.html',
                         user_agent=user_agent,
                         remote_ip=remote_ip,
                         host=host,
                         aluno=ALUNO,
                         titulo='Contexto da requisição')

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

if __name__ == '__main__':
    app.run(debug=True)
