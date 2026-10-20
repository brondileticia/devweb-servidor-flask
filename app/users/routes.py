"""
Rotas de gerenciamento de usuários.
"""
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for

from app.users import bp
from app import db
from app.models import Usuario
from app.services.email_service import enviar_email_novo_usuario


@bp.route('/', methods=['GET', 'POST'])
def banco_dados():
    from flask import current_app
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        funcao = request.form.get('funcao', 'User').strip()
        enviar_professor = request.form.get('enviar_professor') == 'on'
        
        funcoes_validas = current_app.config['FUNCOES']
        
        if not nome:
            flash('Por favor, informe um nome!', 'danger')
            return redirect(url_for('users.banco_dados'))
        
        if funcao not in funcoes_validas:
            funcao = 'User'
        
        existente = Usuario.query.filter(
            db.func.lower(Usuario.nome) == db.func.lower(nome)
        ).first()
        
        if existente:
            existente.funcao = funcao
            existente.atualizado_em = datetime.utcnow()
            db.session.commit()
            flash(f'Usuário "{nome}" já existe! Função atualizada!', 'warning')
        else:
            novo = Usuario(nome, funcao)
            db.session.add(novo)
            db.session.commit()
            
            enviado = enviar_email_novo_usuario(nome, funcao,
                                                enviar_para_professor=enviar_professor)
            
            if enviado:
                if enviar_professor:
                    flash(f'Usuário "{nome}" criado! E-mail enviado para você e para o professor.', 'success')
                else:
                    flash(f'Usuário "{nome}" criado! E-mail enviado apenas para você.', 'success')
            else:
                flash(f'Usuário "{nome}" criado! (E-mail não enviado)', 'info')
        
        return redirect(url_for('users.banco_dados'))
    
    usuarios = Usuario.query.order_by(Usuario.id.desc()).all()
    
    # Agrupa por função
    usuarios_por_funcao = {}
    for funcao in current_app.config['FUNCOES']:
        grupo = Usuario.query.filter_by(funcao=funcao).order_by(Usuario.nome).all()
        if grupo:
            usuarios_por_funcao[funcao] = grupo
    
    # Estatísticas
    contagem_por_funcao = {f: Usuario.query.filter_by(funcao=f).count()
                          for f in current_app.config['FUNCOES']}
    total_usuarios = Usuario.query.count()
    funcoes_em_uso = sum(1 for q in contagem_por_funcao.values() if q > 0)
    
    return render_template('banco_dados.html',
                         usuarios=usuarios,
                         usuarios_por_funcao=usuarios_por_funcao,
                         total_usuarios=total_usuarios,
                         total_funcoes=len(current_app.config['FUNCOES']),
                         funcoes_em_uso=funcoes_em_uso,
                         contagem_por_funcao=contagem_por_funcao,
                         total_admins=contagem_por_funcao.get('Administrator', 0),
                         total_moderators=contagem_por_funcao.get('Moderator', 0),
                         total_users=contagem_por_funcao.get('User', 0),
                         current_time=datetime.utcnow(),
                         titulo='Banco de Dados')


@bp.route('/deletar-usuario/<int:usuario_id>')
def deletar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        nome = usuario.nome
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário "{nome}" deletado!', 'danger')
    else:
        flash('Usuário não encontrado!', 'danger')
    return redirect(url_for('users.banco_dados'))


@bp.route('/promover-usuario/<int:usuario_id>')
def promover_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        antiga = usuario.funcao
        usuario.promover()
        flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'success')
    return redirect(url_for('users.banco_dados'))


@bp.route('/rebaixar-usuario/<int:usuario_id>')
def rebaixar_usuario(usuario_id):
    usuario = Usuario.query.get(usuario_id)
    if usuario:
        antiga = usuario.funcao
        usuario.rebaixar()
        flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'warning')
    return redirect(url_for('users.banco_dados'))
