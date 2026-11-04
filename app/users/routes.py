"""
Rotas de gerenciamento de usuários.
CRUD completo + edição via formulário.
"""
from datetime import datetime
from flask import render_template, request, flash, redirect, url_for, current_app

from app.users import bp
from app import db
from app.models import Usuario
from app.services.email_service import enviar_email_novo_usuario


# ============ LISTAGEM + CADASTRO ============

@bp.route('/', methods=['GET', 'POST'])
def banco_dados():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        funcao = request.form.get('funcao', 'User').strip()
        email_adicional = request.form.get('email_adicional', '').strip()
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
            novo = Usuario(nome, funcao=funcao)
            db.session.add(novo)
            db.session.commit()

            resultado = enviar_email_novo_usuario(
                nome, funcao,
                email_adicional=email_adicional if email_adicional else None,
                enviar_para_professor=enviar_professor
            )

            if resultado['sucesso']:
                msg = f'Usuário "{nome}" criado! E-mail enviado para {len(resultado["destinatarios"])} destinatário(s).'
                detalhes = []
                if resultado.get('enviado_professor'):
                    detalhes.append("professor")
                if resultado.get('email_adicional_valido'):
                    detalhes.append(email_adicional)
                if detalhes:
                    msg += f' Incluindo: {", ".join(detalhes)}.'
                if email_adicional and not resultado.get('email_adicional_valido'):
                    msg += ' (e-mail adicional inválido, ignorado)'
                flash(msg, 'success')
            else:
                flash(f'Usuário "{nome}" criado! (E-mail não enviado: {resultado.get("erro")})', 'warning')

        return redirect(url_for('users.banco_dados'))

    # ============ GET ============
    funcoes = current_app.config['FUNCOES']

    # Agrupa do maior para o menor cargo (Administrator primeiro)
    usuarios_por_funcao = {}
    for funcao in reversed(funcoes):
        grupo = Usuario.query.filter_by(funcao=funcao).order_by(Usuario.nome).all()
        if grupo:
            usuarios_por_funcao[funcao] = grupo

    contagem_por_funcao = {f: Usuario.query.filter_by(funcao=f).count() for f in funcoes}
    total_usuarios = Usuario.query.count()
    funcoes_em_uso = sum(1 for q in contagem_por_funcao.values() if q > 0)

    return render_template('banco_dados.html',
                           usuarios_por_funcao=usuarios_por_funcao,
                           total_usuarios=total_usuarios,
                           total_funcoes=len(funcoes),
                           funcoes_em_uso=funcoes_em_uso,
                           contagem_por_funcao=contagem_por_funcao,
                           titulo='Banco de Dados')


# ============ EDIÇÃO ============

@bp.route('/editar-usuario/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    """Edita um usuário existente (nome e função)."""
    usuario = db.get_or_404(Usuario, usuario_id)
    funcoes_validas = current_app.config['FUNCOES']

    if request.method == 'POST':
        novo_nome = request.form.get('nome', '').strip()
        nova_funcao = request.form.get('funcao', 'User').strip()

        if not novo_nome:
            flash('O nome não pode ser vazio!', 'danger')
            return redirect(url_for('users.editar_usuario', usuario_id=usuario.id))

        if nova_funcao not in funcoes_validas:
            nova_funcao = 'User'

        # Verifica se o novo nome já existe em OUTRO usuário
        duplicado = Usuario.query.filter(
            db.func.lower(Usuario.nome) == db.func.lower(novo_nome),
            Usuario.id != usuario.id
        ).first()

        if duplicado:
            flash(f'Já existe outro usuário com o nome "{novo_nome}"!', 'danger')
            return redirect(url_for('users.editar_usuario', usuario_id=usuario.id))

        nome_antigo = usuario.nome
        funcao_antiga = usuario.funcao

        usuario.nome = novo_nome
        usuario.funcao = nova_funcao
        db.session.commit()

        mudancas = []
        if nome_antigo != novo_nome:
            mudancas.append(f'nome: "{nome_antigo}" → "{novo_nome}"')
        if funcao_antiga != nova_funcao:
            mudancas.append(f'função: {funcao_antiga} → {nova_funcao}')

        if mudancas:
            flash(f'Usuário atualizado! ({"; ".join(mudancas)})', 'success')
        else:
            flash('Nenhuma alteração foi feita.', 'info')

        return redirect(url_for('users.banco_dados'))

    return render_template('editar_usuario.html', usuario=usuario, titulo='Editar Usuário')


# ============ EXCLUSÃO ============
# Ações que alteram dados usam POST: um link GET pode ser disparado
# sem querer (pré-carregamento do navegador, robôs, histórico).

@bp.route('/deletar-usuario/<int:usuario_id>', methods=['POST'])
def deletar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario:
        nome = usuario.nome
        db.session.delete(usuario)
        db.session.commit()
        flash(f'Usuário "{nome}" deletado com sucesso!', 'success')
    else:
        flash('Usuário não encontrado!', 'danger')
    return redirect(url_for('users.banco_dados'))


# ============ PROMOVER / REBAIXAR ============

@bp.route('/promover-usuario/<int:usuario_id>', methods=['POST'])
def promover_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario:
        antiga = usuario.funcao
        if usuario.promover():
            flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'success')
        else:
            flash(f'"{usuario.nome}" já está no cargo mais alto.', 'info')
    return redirect(url_for('users.banco_dados'))


@bp.route('/rebaixar-usuario/<int:usuario_id>', methods=['POST'])
def rebaixar_usuario(usuario_id):
    usuario = db.session.get(Usuario, usuario_id)
    if usuario:
        antiga = usuario.funcao
        if usuario.rebaixar():
            flash(f'"{usuario.nome}": {antiga} → {usuario.funcao}', 'warning')
        else:
            flash(f'"{usuario.nome}" já está no cargo mais baixo.', 'info')
    return redirect(url_for('users.banco_dados'))


# ============ TESTE DE E-MAIL ============

@bp.route('/testar-email', methods=['POST'])
def testar_email():
    email_extra = request.form.get('email', '').strip()
    enviar_professor = request.form.get('professor') == 'on'

    resultado = enviar_email_novo_usuario(
        "UsuarioTeste", "User",
        email_adicional=email_extra if email_extra else None,
        enviar_para_professor=enviar_professor
    )

    if resultado['sucesso']:
        flash(f'E-mail de teste enviado para {len(resultado["destinatarios"])} destinatário(s)!', 'success')
    else:
        flash(f'Falha ao enviar: {resultado.get("erro")}', 'danger')

    return redirect(url_for('users.banco_dados'))
