"""
Rotas de autenticação (login/logout).
"""
from datetime import datetime
from flask import render_template, request, session, flash, redirect, url_for

from app.auth import bp


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario', '').strip()
        senha = request.form.get('senha', '').strip()
        
        if usuario == 'admin' and senha == '123456':
            session['usuario_logado'] = usuario
            flash(f'Login realizado! Bem-vindo(a), {usuario}!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Usuário ou senha inválidos!', 'danger')
    
    return render_template('login.html',
                         current_time=datetime.utcnow(),
                         titulo='Login')


@bp.route('/logout')
def logout():
    session.clear()
    flash('Logout realizado!', 'info')
    return redirect(url_for('main.home'))
