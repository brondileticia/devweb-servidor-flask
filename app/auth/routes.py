from datetime import datetime
from flask import (render_template, request, flash, redirect, 
                   url_for, session, current_app)
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import bp
from app import db
from app.models import Usuario
from app.services.email_service import enviar_email_confirmacao, enviar_email_reset_senha


# ============ LOGIN ============

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip().lower()
        senha = request.form.get('senha', '')
        
        # Busca por email OU username
        usuario = Usuario.query.filter(
            (Usuario.email == identificador) | (Usuario.username == identificador)
        ).first()
        
        if usuario and usuario.check_password(senha):
            if not usuario.email_confirmado:
                flash('Confirme seu e-mail antes de fazer login. Verifique sua caixa de entrada.', 'warning')
                return redirect(url_for('auth.login'))
            
            login_user(usuario)
            flash(f'Bem-vindo(a), {usuario.nome}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.home'))
        else:
            flash('E-mail/usuário ou senha inválidos.', 'danger')
    
    return render_template('auth/login.html', titulo='Login')


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
        
        erros = []
        
        if not nome or len(nome) < 3:
            erros.append('Nome deve ter pelo menos 3 caracteres.')
        
        if not email or '@' not in email:
            erros.append('E-mail inválido.')
        
        # Validação de username (recomendação)
        if not username or len(username) < 3:
            erros.append('Nome de usuário deve ter pelo menos 3 caracteres.')
        elif not username.replace('_', '').isalnum():
            erros.append('Nome de usuário deve conter apenas letras, números e underline (_).')
        elif username[0].isdigit():
            erros.append('Nome de usuário não pode começar com número.')
        
        if len(senha) < 8:
            erros.append('Senha deve ter pelo menos 8 caracteres.')
        
        if senha != confirmacao:
            erros.append('Senhas não conferem.')
        
        # Verifica duplicatas
        if Usuario.query.filter_by(email=email).first():
            erros.append('Este e-mail já está cadastrado.')
        if Usuario.query.filter_by(username=username).first():
            erros.append('Este nome de usuário já está em uso.')
        
        if erros:
            for erro in erros:
                flash(erro, 'danger')
            return render_template('auth/cadastro.html', titulo='Cadastro',
                                 nome=nome, email=email, username=username)
        
        # Cria usuário
        novo = Usuario(nome, email, username, senha)
        db.session.add(novo)
        db.session.commit()
        
        # Envia e-mail de confirmação
        enviar_email_confirmacao(novo)
        
        flash('Conta criada! Verifique seu e-mail para confirmar o cadastro.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/cadastro.html', titulo='Cadastro')


# ============ CONFIRMAÇÃO DE E-MAIL ============

@bp.route('/confirmar/<token>')
def confirmar_email(token):
    usuario = Usuario.query.filter_by(token_confirmacao=token).first()
    
    if not usuario:
        flash('Link de confirmação inválido ou expirado.', 'danger')
        return redirect(url_for('auth.login'))
    
    if usuario.confirmar_email(token):
        flash('E-mail confirmado com sucesso! Você já pode fazer login.', 'success')
    else:
        flash('Erro ao confirmar e-mail.', 'danger')
    
    return redirect(url_for('auth.login'))


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
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            token = usuario.gerar_token_reset()
            enviar_email_reset_senha(usuario, token)
        
        # Sempre mostra a mesma mensagem (segurança: não revela se o e-mail existe)
        flash('Se o e-mail estiver cadastrado, você receberá instruções para redefinir a senha.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/esqueci_senha.html', titulo='Esqueci minha senha')


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
        
        if len(nova_senha) < 8:
            flash('Senha deve ter pelo menos 8 caracteres.', 'danger')
            return render_template('auth/resetar_senha.html', token=token, titulo='Redefinir senha')
        
        if nova_senha != confirmacao:
            flash('Senhas não conferem.', 'danger')
            return render_template('auth/resetar_senha.html', token=token, titulo='Redefinir senha')
        
        usuario.resetar_senha(nova_senha)
        flash('Senha redefinida com sucesso! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/resetar_senha.html', token=token, titulo='Redefinir senha')


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
        
        if len(nova_senha) < 8:
            flash('Nova senha deve ter pelo menos 8 caracteres.', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        if nova_senha != confirmacao:
            flash('Senhas não conferem.', 'danger')
            return redirect(url_for('auth.alterar_senha'))
        
        current_user.set_password(nova_senha)
        db.session.commit()
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('main.home'))
    
    return render_template('auth/alterar_senha.html', titulo='Alterar senha')


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
        
        if '@' not in novo_email:
            flash('E-mail inválido.', 'danger')
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
    
    return render_template('auth/alterar_email.html', titulo='Alterar e-mail')


@bp.route('/confirmar-novo-email/<token>')
@login_required
def confirmar_novo_email(token):
    if session.get('token_novo_email') != token:
        flash('Token inválido.', 'danger')
        return redirect(url_for('main.home'))
    
    novo_email = session.get('novo_email_pendente')
    if not novo_email:
        flash('Nenhuma alteração pendente.', 'warning')
        return redirect(url_for('main.home'))
    
    current_user.email = novo_email
    db.session.commit()
    
    session.pop('novo_email_pendente', None)
    session.pop('token_novo_email', None)
    
    flash('E-mail alterado com sucesso!', 'success')
    return redirect(url_for('main.home'))
