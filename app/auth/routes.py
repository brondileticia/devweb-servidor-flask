import secrets
from urllib.parse import urlparse

from flask import render_template, request, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import bp
from app import db, login_manager
from app.models import Usuario
from app.services.email_service import (
    enviar_email_confirmacao,
    enviar_email_reset_senha,
    enviar_email_confirmacao_novo_email,
    enviar_email_aviso_senha_alterada,
)
from app.services.validation_service import (
    validar_cadastro,
    validar_email,
    validar_senha,
    validar_confirmacao_senha,
)


def _url_segura(destino):
    """Aceita só caminhos internos (evita redirecionar para outro site)."""
    if not destino:
        return None
    partes = urlparse(destino)
    if partes.netloc or partes.scheme or not destino.startswith('/'):
        return None
    return destino


# ============================================================
# SEMANA 16 — CONTROLE DE ACESSO GLOBAL
# ============================================================
# Em vez de colocar @login_required em cada rota (e correr o risco de
# esquecer uma), um único "porteiro" roda ANTES de toda requisição.
#
#   Anônimo ............ só vê a home ("Olá, Desconhecido!") e as telas de conta
#   Logado sem confirmar só vê a home com o aviso + reenviar confirmação + sair
#   Logado e confirmado  vê tudo

# Telas que qualquer pessoa pode abrir (inclusive sem login)
ENDPOINTS_PUBLICOS = {
    'static',
    'main.home',
    'auth.login',
    'auth.cadastro',
    'auth.confirmar_email',
    'auth.esqueci_senha',
    'auth.resetar_senha',
}

# Telas extras liberadas para quem está logado mas ainda não confirmou
ENDPOINTS_NAO_CONFIRMADO = {
    'auth.logout',
    'auth.reenviar_confirmacao',
}


@bp.before_app_request
def controlar_acesso():
    """Roda antes de QUALQUER rota da aplicação (before_APP_request)."""
    endpoint = request.endpoint

    # endpoint None = URL inexistente: deixa o Flask responder 404
    if endpoint is None or endpoint in ENDPOINTS_PUBLICOS:
        return None

    if not current_user.is_authenticated:
        # Mesmo comportamento do @login_required: flash + redirect para o login
        # com ?next=/pagina-pedida, para voltar para lá depois de entrar.
        return login_manager.unauthorized()

    if not current_user.email_confirmado and endpoint not in ENDPOINTS_NAO_CONFIRMADO:
        flash('Você não pode acessar esta página antes de confirmar seu e-mail.', 'warning')
        return redirect(url_for('main.home'))

    return None  # None = segue para a rota normalmente


def _enviar_confirmacao_com_feedback(usuario, msg_sucesso):
    """Envia o e-mail de confirmação e mostra a mensagem adequada ao resultado."""
    resultado = enviar_email_confirmacao(usuario)
    if resultado['sucesso']:
        flash(msg_sucesso, 'success')
    elif current_app.debug:
        # Só em desenvolvimento: sem Mailgun configurado, mostra o link na tela
        link = url_for('auth.confirmar_email', token=usuario.token_confirmacao, _external=True)
        flash('O e-mail não foi enviado (modo desenvolvimento). '
              f'Confirme por este link: {link}', 'warning')
    else:
        flash('Não foi possível enviar o e-mail de confirmação agora. '
              'Tente novamente em alguns minutos.', 'warning')


# ============ LOGIN ============

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip().lower()
        senha = request.form.get('senha', '')
        lembrar = request.form.get('lembrar') == 'on'

        # Busca por email OU username
        usuario = Usuario.query.filter(
            (Usuario.email == identificador) | (Usuario.username == identificador)
        ).first()

        if usuario and usuario.check_password(senha):
            # Semana 16: quem não confirmou TAMBÉM entra — mas cai na home
            # com o aviso e sem acesso ao restante (ver controlar_acesso).
            login_user(usuario, remember=lembrar)

            if not usuario.email_confirmado:
                flash('Sua conta ainda não foi confirmada. Você não pode acessar o sistema '
                      'antes de confirmar o e-mail.', 'warning')
                return redirect(url_for('main.home'))

            flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
            next_page = _url_segura(request.args.get('next'))
            return redirect(next_page or url_for('main.home'))

        flash('E-mail/usuário ou senha inválidos.', 'danger')
        return render_template('login.html', titulo='Login', identificador=identificador)

    return render_template('login.html', titulo='Login')


# ============ CADASTRO ============

@bp.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip().lower()
        senha = request.form.get('senha', '')
        confirmacao = request.form.get('confirmacao', '')

        # Usa o serviço de validação centralizado
        _, erros = validar_cadastro(nome, email, username, senha, confirmacao)

        if email and Usuario.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado.')
        if username and Usuario.query.filter_by(username=username).first():
            erros.append('Este nome de usuário já está em uso.')

        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('cadastro.html', titulo='Cadastro',
                                   nome=nome, email=email, username=username)

        novo = Usuario(nome, email=email, username=username, password=senha)
        db.session.add(novo)
        db.session.commit()

        _enviar_confirmacao_com_feedback(
            novo, 'Conta criada! Verifique seu e-mail para confirmar o cadastro.')
        return redirect(url_for('auth.login'))

    return render_template('cadastro.html', titulo='Cadastro')


# ============ CONFIRMAÇÃO DE E-MAIL ============

@bp.route('/confirmar/<token>')
def confirmar_email(token):
    usuario = Usuario.query.filter_by(token_confirmacao=token).first()

    if usuario and usuario.confirmar_email(token):
        if current_user.is_authenticated and current_user.id == usuario.id:
            flash('E-mail confirmado! Seu acesso foi liberado.', 'success')
            return redirect(url_for('main.home'))
        flash('E-mail confirmado com sucesso! Você já pode fazer login.', 'success')
    else:
        flash('Link de confirmação inválido ou já utilizado.', 'danger')

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    return redirect(url_for('auth.login'))


@bp.route('/reenviar-confirmacao', methods=['POST'])
@login_required
def reenviar_confirmacao():
    """Gera um token novo (invalida o anterior) e reenvia o e-mail."""
    if current_user.email_confirmado:
        flash('Sua conta já está confirmada.', 'info')
        return redirect(url_for('main.home'))

    current_user.gerar_token_confirmacao()
    db.session.commit()
    _enviar_confirmacao_com_feedback(
        current_user, f'Enviamos um novo link de confirmação para {current_user.email}.')
    return redirect(url_for('main.home'))


# ============ LOGOUT ============

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout realizado com sucesso.', 'info')
    return redirect(url_for('main.home'))


# ============ ESQUECI MINHA SENHA ============

@bp.route('/esqueci-senha', methods=['GET', 'POST'])
def esqueci_senha():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        usuario = Usuario.query.filter_by(email=email).first() if email else None

        if usuario and usuario.pode_logar:
            token = usuario.gerar_token_reset()
            enviar_email_reset_senha(usuario, token)

        # Sempre mostra a mesma mensagem (segurança: não revela se o e-mail existe)
        flash('Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha.', 'info')
        return redirect(url_for('auth.login'))

    return render_template('esqueci_senha.html', titulo='Esqueci minha senha')


# ============ REDEFINIR SENHA ============

@bp.route('/resetar-senha/<token>', methods=['GET', 'POST'])
def resetar_senha(token):
    usuario = Usuario.query.filter_by(token_reset=token).first()

    if not usuario or not usuario.validar_token_reset(token):
        flash('Link inválido ou expirado. Solicite um novo.', 'danger')
        return redirect(url_for('auth.esqueci_senha'))

    if request.method == 'POST':
        nova_senha = request.form.get('senha', '')
        confirmacao = request.form.get('confirmacao', '')

        for valido, erro in (validar_senha(nova_senha),
                             validar_confirmacao_senha(nova_senha, confirmacao)):
            if not valido:
                flash(erro, 'danger')
                return render_template('resetar_senha.html', token=token, titulo='Redefinir senha')

        usuario.resetar_senha(nova_senha)
        enviar_email_aviso_senha_alterada(usuario)
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('resetar_senha.html', token=token, titulo='Redefinir senha')


# ============ ALTERAR SENHA (logado) ============

@bp.route('/alterar-senha', methods=['GET', 'POST'])
@login_required
def alterar_senha():
    if request.method == 'POST':
        senha_atual = request.form.get('senha_atual', '')
        nova_senha = request.form.get('nova_senha', '')
        confirmacao = request.form.get('confirmacao', '')

        if not current_user.check_password(senha_atual):
            flash('Senha atual incorreta.', 'danger')
            return redirect(url_for('auth.alterar_senha'))

        for valido, erro in (validar_senha(nova_senha),
                             validar_confirmacao_senha(nova_senha, confirmacao)):
            if not valido:
                flash(erro, 'danger')
                return redirect(url_for('auth.alterar_senha'))

        current_user.set_password(nova_senha)
        db.session.commit()
        enviar_email_aviso_senha_alterada(current_user)
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('main.home'))

    return render_template('alterar_senha.html', titulo='Alterar senha')


# ============ ALTERAR E-MAIL ============

@bp.route('/alterar-email', methods=['GET', 'POST'])
@login_required
def alterar_email():
    if request.method == 'POST':
        novo_email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')

        if not current_user.check_password(senha):
            flash('Senha incorreta.', 'danger')
            return redirect(url_for('auth.alterar_email'))

        valido, erro = validar_email(novo_email)
        if not valido:
            flash(erro, 'danger')
            return redirect(url_for('auth.alterar_email'))

        if Usuario.query.filter_by(email=novo_email).first():
            flash('Este e-mail já está em uso.', 'danger')
            return redirect(url_for('auth.alterar_email'))

        # Gera token para o NOVO e-mail
        token = secrets.token_urlsafe(32)
        session['novo_email_pendente'] = novo_email
        session['token_novo_email'] = token

        enviar_email_confirmacao_novo_email(current_user, novo_email, token)

        flash(f'Um link de confirmação foi enviado para {novo_email}. Confirme para efetivar a troca.', 'info')
        return redirect(url_for('main.home'))

    return render_template('alterar_email.html', titulo='Alterar e-mail')


@bp.route('/confirmar-novo-email/<token>')
@login_required
def confirmar_novo_email(token):
    token_sessao = session.get('token_novo_email')
    novo_email = session.get('novo_email_pendente')

    if not token_sessao or not secrets.compare_digest(token_sessao, token) or not novo_email:
        flash('Link inválido ou nenhuma alteração pendente.', 'danger')
        return redirect(url_for('main.home'))

    # Alguém pode ter usado esse e-mail enquanto o link não era clicado
    if Usuario.query.filter_by(email=novo_email).first():
        flash('Este e-mail já está em uso por outra conta.', 'danger')
        return redirect(url_for('main.home'))

    current_user.email = novo_email
    db.session.commit()

    session.pop('novo_email_pendente', None)
    session.pop('token_novo_email', None)

    flash('E-mail alterado com sucesso!', 'success')
    return redirect(url_for('main.home'))
