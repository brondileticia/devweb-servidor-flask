"""
Rotas principais: Home, Data/Hora, Identificação, etc.
"""
from datetime import datetime
from flask import render_template, session, request, flash, redirect, url_for

from app.main import bp


@bp.route('/')
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
         'url': '/banco-dados/', 'icone': 'glyphicon-hdd', 'cor': 'panel-primary', 'aula': 'Semana 12'},
        {'titulo': 'E-mails Enviados', 'descricao': 'Histórico de e-mails enviados',
         'url': '/emailsEnviados', 'icone': 'glyphicon-envelope', 'cor': 'panel-success', 'aula': 'Semana 12'},
        {'titulo': 'Formulário Simples', 'descricao': 'Formulário básico',
         'url': '/formulario', 'icone': 'glyphicon-pencil', 'cor': 'panel-default', 'aula': 'Extra'}
    ]
    return render_template('home.html', paginas=paginas,
                         current_time=datetime.utcnow(), titulo='Home')


@bp.route('/data-hora')
def data_hora():
    return render_template('data_hora.html',
                         current_time=datetime.utcnow(),
                         titulo='Data e Hora')


@bp.route('/identificacao')
def identificacao():
    return render_template('identificacao.html', titulo='Identificação do Aluno')


@bp.route('/contextorequisicao')
def contextorequisicao():
    return render_template('contextorequisicao.html',
                         user_agent=request.headers.get('User-Agent', 'Desconhecido'),
                         remote_ip=request.remote_addr or 'Desconhecido',
                         host=request.host or 'Desconhecido',
                         titulo='Contexto da Requisição')


@bp.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
    from flask import current_app
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
            return redirect(url_for('main.formulario_identificacao'))
        
        session['nome'] = nome
        session['sobrenome'] = sobrenome
        session['instituicao'] = instituicao if instituicao else None
        session['disciplina'] = disciplina
        
        flash(f'Dados atualizados! Bem-vindo(a), {nome} {sobrenome}!', 'success')
        return redirect(url_for('main.formulario_identificacao'))
    
    nome_completo = f"{nome} {sobrenome}".strip() if nome else None
    
    return render_template('formulario_identificacao.html',
                         nome=nome, sobrenome=sobrenome,
                         nome_completo=nome_completo,
                         instituicao=instituicao, disciplina=disciplina,
                         disciplinas=current_app.config['DISCIPLINAS'],
                         current_time=datetime.utcnow(),
                         titulo='Formulário de Identificação')


@bp.route('/formulario', methods=['GET', 'POST'])
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
        return redirect(url_for('main.formulario'))
    
    nome_atual = session.get('nome_usuario', None)
    return render_template('formulario.html', nome=nome_atual, titulo='Formulário Simples')


@bp.route('/user/<name>')
def user(name):
    name = name.replace('<', '').replace('>', '').strip()
    return render_template('user.html', name=name, titulo=f'Usuário {name}')
