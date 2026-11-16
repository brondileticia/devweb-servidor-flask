"""
Rotas principais: Home, Data/Hora, Identificação, etc.
"""
import ipaddress
from datetime import datetime

from flask import render_template, session, request, flash, redirect, url_for, current_app
from flask_login import current_user

from app import db
from app.main import bp
from app.models import Usuario


@bp.route('/')
def home():
    """
    Semana 16: a mesma URL mostra três coisas diferentes, conforme quem acessa.

    - anônimo ............ "Olá, Desconhecido!" e nada mais
    - logado sem confirmar "Olá, Fulano!" + aviso de que precisa confirmar
    - logado e confirmado  relação de usuários cadastrados + atividades

    A relação só é CONSULTADA no banco quando o acesso é liberado. Esconder só no
    template não basta: o dado nem deve sair do servidor para quem não pode vê-lo.
    """
    usuarios = []
    if current_user.is_authenticated and current_user.email_confirmado:
        usuarios = Usuario.query.order_by(db.func.lower(Usuario.nome)).all()

    return render_template('home.html',
                           usuarios=usuarios,
                           total_confirmados=sum(1 for u in usuarios if u.email_confirmado),
                           current_time=datetime.utcnow(),
                           titulo='Início')


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
