"""
Rotas principais: Home, Data/Hora, Identificação, etc.
"""
import ipaddress
from datetime import datetime
from flask import render_template, session, request, flash, redirect, url_for, current_app

from app.main import bp


@bp.route('/')
def home():
    paginas = [
        {'titulo': 'Data e Hora', 'descricao': 'Data, hora e informações temporais com Moment.js',
         'endpoint': 'main.data_hora', 'icone': 'bi-clock', 'cor': 'primary', 'aula': 'Aula 040'},
        {'titulo': 'Identificação do Aluno', 'descricao': 'Dados do aluno e do campus',
         'endpoint': 'main.identificacao', 'icone': 'bi-person-vcard', 'cor': 'success', 'aula': 'Aula 040'},
        {'titulo': 'Contexto da Requisição', 'descricao': 'User-Agent, IP e host da requisição HTTP',
         'endpoint': 'main.contextorequisicao', 'icone': 'bi-hdd-network', 'cor': 'info', 'aula': 'Aula 040'},
        {'titulo': 'Formulário de Identificação', 'descricao': 'Nome, instituição e disciplina na sessão',
         'endpoint': 'main.formulario_identificacao', 'icone': 'bi-ui-checks', 'cor': 'warning', 'aula': 'Aula 050.B'},
        {'titulo': 'Login', 'descricao': 'Autenticação com Flask-Login e confirmação por e-mail',
         'endpoint': 'auth.login', 'icone': 'bi-box-arrow-in-right', 'cor': 'danger', 'aula': 'Aula 050.B'},
        {'titulo': 'Banco de Dados', 'descricao': 'Usuários agrupados por função (CRUD)',
         'endpoint': 'users.banco_dados', 'icone': 'bi-database', 'cor': 'primary', 'aula': 'Semana 12'},
        {'titulo': 'E-mails Enviados', 'descricao': 'Histórico de e-mails enviados pelo Mailgun',
         'endpoint': 'emails.emails_enviados', 'icone': 'bi-envelope-paper', 'cor': 'success', 'aula': 'Semana 12'},
        {'titulo': 'Formulário Simples', 'descricao': 'Padrão Post/Redirect/Get com sessão',
         'endpoint': 'main.formulario', 'icone': 'bi-pencil-square', 'cor': 'secondary', 'aula': 'Extra'},
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
    remote_ip = request.remote_addr or 'Desconhecido'
    try:
        ip_privado = ipaddress.ip_address(remote_ip).is_private
    except ValueError:
        ip_privado = None

    return render_template('contextorequisicao.html',
                           user_agent=request.headers.get('User-Agent', 'Desconhecido'),
                           remote_ip=remote_ip,
                           ip_privado=ip_privado,
                           host=request.host or 'Desconhecido',
                           metodo=request.method,
                           protocolo=request.environ.get('SERVER_PROTOCOL', 'HTTP/1.1'),
                           titulo='Contexto da Requisição')


@bp.route('/formulario-identificacao', methods=['GET', 'POST'])
def formulario_identificacao():
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
        session['instituicao'] = instituicao or None
        session['disciplina'] = disciplina

        flash(f'Dados atualizados! Bem-vindo(a), {nome} {sobrenome}!', 'success')
        return redirect(url_for('main.formulario_identificacao'))

    nome = session.get('nome', '')
    sobrenome = session.get('sobrenome', '')
    nome_completo = f"{nome} {sobrenome}".strip() or None

    return render_template('formulario_identificacao.html',
                           nome=nome, sobrenome=sobrenome,
                           nome_completo=nome_completo,
                           instituicao=session.get('instituicao'),
                           disciplina=session.get('disciplina', ''),
                           disciplinas=current_app.config['DISCIPLINAS'],
                           remote_ip=request.remote_addr,
                           host=request.host,
                           current_time=datetime.utcnow(),
                           titulo='Formulário de Identificação')


@bp.route('/formulario-identificacao/limpar', methods=['POST'])
def limpar_identificacao():
    for chave in ('nome', 'sobrenome', 'instituicao', 'disciplina'):
        session.pop(chave, None)
    flash('Dados de identificação apagados.', 'info')
    return redirect(url_for('main.formulario_identificacao'))


@bp.route('/formulario', methods=['GET', 'POST'])
def formulario():
    nome_atual = session.get('nome_usuario')

    if request.method == 'POST':
        if request.form.get('acao') == 'limpar':
            session.pop('nome_usuario', None)
            flash('Nome apagado.', 'info')
            return redirect(url_for('main.formulario'))

        novo_nome = request.form.get('nome', '').strip()
        if novo_nome:
            if nome_atual and nome_atual != novo_nome:
                flash(f'Parece que você mudou seu nome: "{nome_atual}" → "{novo_nome}"', 'warning')
                historico = session.get('historico_nomes', [])
                historico.append(nome_atual)
                session['historico_nomes'] = historico[-5:]
            elif not nome_atual:
                flash(f'Bem-vindo(a), {novo_nome}!', 'success')
            session['nome_usuario'] = novo_nome
        return redirect(url_for('main.formulario'))

    return render_template('formulario.html', nome=nome_atual, titulo='Formulário Simples')


@bp.route('/user/<name>')
def user(name):
    # O Jinja2 já escapa o HTML automaticamente; aqui só limpamos espaços
    name = name.strip()
    return render_template('user.html', name=name, titulo=f'Usuário {name}')
