"""
Serviço responsável pelo envio e persistência de e-mails.
Semana 15: cadastro administrativo, confirmação de conta, reset de senha,
confirmação de novo e-mail e aviso de troca de senha.
"""
from datetime import datetime
import requests
from flask import current_app, url_for

from app import db
from app.models import EmailEnviado
from app.services.validation_service import validar_email


# ============================================================
# FUNÇÃO INTERNA DE ENVIO
# ============================================================

def _enviar_email_generico(destinatarios, assunto, html, texto_curto=None):
    """
    Função interna para envio via Mailgun + persistência no banco.
    
    Args:
        destinatarios: str ou list de e-mails
        assunto: str
        html: str (corpo HTML)
        texto_curto: str (resumo, para persistência — se None, usa o assunto)
    
    Returns:
        dict: {'sucesso': bool, 'erro': str|None, 'destinatarios': list}
    """
    api_key = current_app.config['MAILGUN_API_KEY']
    domain = current_app.config['MAILGUN_DOMAIN']
    
    if not api_key:
        print("⚠️ API key do Mailgun não configurada.")
        return {
            'sucesso': False,
            'erro': 'API key não configurada',
            'destinatarios': []
        }
    
    # Normaliza destinatários em lista
    if isinstance(destinatarios, str):
        destinatarios = [destinatarios]
    
    # Remove duplicatas mantendo a ordem
    destinatarios = list(dict.fromkeys(destinatarios))
    
    from_addr = f"PTBDSWS <postmaster@{domain}>"
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    sucesso = False
    erro = None
    
    try:
        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": from_addr,
                "to": destinatarios,
                "subject": assunto,
                "html": html
            },
            timeout=10
        )
        sucesso = response.status_code == 200
        
        if sucesso:
            print(f"✅ E-mail enviado para {destinatarios}")
        else:
            erro = f"{response.status_code} - {response.text}"
            print(f"❌ Erro Mailgun: {erro}")
    except Exception as e:
        erro = str(e)
        print(f"❌ Erro ao enviar e-mail: {e}")
    
    # ============ PERSISTÊNCIA ============
    try:
        registro = EmailEnviado(
            remetente=from_addr,
            destinatarios=str(destinatarios),
            assunto=assunto,
            texto=texto_curto or assunto,
            sucesso=sucesso
        )
        registro.salvar()
    except Exception as e:
        print(f"⚠️ Erro ao salvar histórico de e-mail: {e}")
    
    return {
        'sucesso': sucesso,
        'erro': erro,
        'destinatarios': destinatarios
    }


# ============================================================
# TEMPLATES HTML PARA E-MAILS
# ============================================================

def _html_base(titulo, saudacao, corpo_html, cor_cabecalho='#2563eb'):
    """Template HTML padrão para todos os e-mails."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background-color: #f8fafc; color: #1e293b; line-height: 1.6;">
        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            
            <!-- Cabeçalho -->
            <div style="background-color: {cor_cabecalho}; padding: 30px 20px; text-align: center;">
                <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 600;">
                    {titulo}
                </h1>
            </div>
            
            <!-- Corpo -->
            <div style="padding: 30px 25px;">
                <p style="margin: 0 0 20px 0; font-size: 16px;">
                    {saudacao}
                </p>
                
                {corpo_html}
                
                <p style="margin: 30px 0 0 0; font-size: 13px; color: #64748b;">
                    Este é um e-mail automático da aplicação <strong>PTBDSWS</strong>. 
                    Por favor, não responda.
                </p>
            </div>
            
            <!-- Rodapé -->
            <div style="background-color: #1e293b; padding: 20px; text-align: center;">
                <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                    <strong style="color: #ffffff;">PTBDSWS</strong> — Programação em Desenvolvimento Web Servidor
                </p>
                <p style="margin: 5px 0 0 0; color: #64748b; font-size: 11px;">
                    4º Semestre — Análise e Desenvolvimento de Sistemas<br>
                    IFSP — Campus Pirituba
                </p>
            </div>
        </div>
    </body>
    </html>
    """


def _botao_html(texto, url, cor='#2563eb'):
    """Gera um botão HTML estilizado."""
    return f"""
    <div style="text-align: center; margin: 25px 0;">
        <a href="{url}" 
           style="display: inline-block; background-color: {cor}; color: #ffffff; 
                  padding: 14px 32px; text-decoration: none; border-radius: 8px; 
                  font-weight: 600; font-size: 15px;">
            {texto}
        </a>
    </div>
    """


def _info_box(conteudo, cor_fundo='#f1f5f9', cor_borda='#2563eb'):
    """Gera uma caixa de informação destacada."""
    return f"""
    <div style="background-color: {cor_fundo}; border-left: 4px solid {cor_borda}; 
                padding: 15px 20px; margin: 20px 0; border-radius: 4px;">
        {conteudo}
    </div>
    """


def _link_texto(url):
    """Gera link de fallback (para clientes que não renderizam botão)."""
    return f"""
    <p style="font-size: 12px; color: #64748b; word-break: break-all; margin-top: 20px;">
        Se o botão não funcionar, copie e cole este link no navegador:<br>
        <a href="{url}" style="color: #2563eb;">{url}</a>
    </p>
    """


# ============================================================
# 1. E-MAIL DE NOVO USUÁRIO (cadastro administrativo)
# ============================================================

def enviar_email_novo_usuario(nome_usuario, funcao, email_adicional=None, enviar_para_professor=False):
    """
    Envia e-mail quando um novo usuário é cadastrado (painel admin).
    
    - SEMPRE envia para o e-mail institucional
    - Envia para o professor SOMENTE se enviar_para_professor=True
    - Opcionalmente envia para um e-mail adicional
    """
    api_key = current_app.config['MAILGUN_API_KEY']
    if not api_key:
        print("⚠️ API key do Mailgun não configurada.")
        return {
            'sucesso': False,
            'destinatarios': [],
            'erro': 'API key não configurada',
            'email_adicional_valido': False,
            'enviado_professor': False
        }
    
    email_institucional = current_app.config['EMAIL_INSTITUCIONAL']
    email_professor = current_app.config['EMAIL_PROFESSOR']
    aluno_nome = current_app.config['ALUNO_NOME']
    aluno_prontuario = current_app.config['ALUNO_PRONTUARIO']
    
    # ============ DESTINATÁRIOS ============
    destinatarios = [email_institucional]
    if enviar_para_professor:
        destinatarios.append(email_professor)
    
    email_adicional_valido = False
    if email_adicional:
        email_adicional = email_adicional.strip()
        # Usa a validação centralizada
        valido, _ = validar_email(email_adicional)
        if valido and email_adicional not in destinatarios:
            destinatarios.append(email_adicional)
            email_adicional_valido = True
    
    # ============ CORPO DO E-MAIL ============
    info_html = _info_box(f"""
        <p style="margin: 5px 0;"><strong>Prontuário do aluno:</strong> {aluno_prontuario}</p>
        <p style="margin: 5px 0;"><strong>Nome do aluno:</strong> {aluno_nome}</p>
        <p style="margin: 5px 0;"><strong>Usuário cadastrado:</strong> {nome_usuario}</p>
        <p style="margin: 5px 0;"><strong>Função:</strong> {funcao}</p>
        <p style="margin: 5px 0;"><strong>Data e hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
    """)
    
    blocos_extra = ""
    if enviar_para_professor:
        blocos_extra += _info_box(
            f'<p style="margin: 0; font-size: 13px;">✉️ Este e-mail também foi enviado para o professor: <strong>{email_professor}</strong></p>',
            '#d1fae5', '#16a34a'
        )
    
    if email_adicional_valido:
        blocos_extra += _info_box(
            f'<p style="margin: 0; font-size: 13px;">✉️ Este e-mail também foi enviado para: <strong>{email_adicional}</strong></p>',
            '#dbeafe', '#2563eb'
        )
    
    html = _html_base(
        titulo="📧 Novo Usuário Cadastrado",
        saudacao="Um novo usuário foi cadastrado no sistema!",
        corpo_html=info_html + blocos_extra
    )
    
    resultado = _enviar_email_generico(
        destinatarios=destinatarios,
        assunto="[Flasky] Novo usuário",
        html=html,
        texto_curto=f"Novo usuário cadastrado: {nome_usuario}"
    )
    
    resultado['email_adicional_valido'] = email_adicional_valido
    resultado['enviado_professor'] = enviar_para_professor
    return resultado


# ============================================================
# 2. E-MAIL DE CONFIRMAÇÃO DE CONTA (novo cadastro)
# ============================================================

def enviar_email_confirmacao(usuario):
    """
    Envia e-mail com link de confirmação de conta após o cadastro.
    
    Args:
        usuario: instância de Usuario (com token_confirmacao)
    
    Returns:
        dict: resultado do envio
    """
    token = usuario.token_confirmacao
    if not token:
        print("⚠️ Usuário sem token de confirmação.")
        return {'sucesso': False, 'erro': 'Sem token', 'destinatarios': []}
    
    # Valida o e-mail antes de enviar
    valido, erro = validar_email(usuario.email)
    if not valido:
        print(f"⚠️ E-mail inválido: {erro}")
        return {'sucesso': False, 'erro': erro, 'destinatarios': []}
    
    link = url_for('auth.confirmar_email', token=token, _external=True)
    
    corpo = f"""
    <p style="margin: 0 0 15px 0; font-size: 15px;">
        Falta apenas um passo para ativar sua conta. Clique no botão abaixo:
    </p>
    
    {_botao_html('✅ Confirmar minha conta', link, '#16a34a')}
    
    {_info_box('''
        <p style="margin: 0; font-size: 13px;">
            <strong>⏱️ Importante:</strong> o link é de uso único. Após confirmar, 
            você poderá fazer login normalmente.
        </p>
    ''', '#fef3c7', '#f59e0b')}
    
    {_link_texto(link)}
    """
    
    html = _html_base(
        titulo="Confirme sua conta",
        saudacao=f"Olá, <strong>{usuario.nome}</strong>!",
        corpo_html=corpo,
        cor_cabecalho='#16a34a'
    )
    
    return _enviar_email_generico(
        destinatarios=usuario.email,
        assunto="Confirme sua conta — PTBDSWS",
        html=html,
        texto_curto=f"Confirmação de conta para {usuario.email}"
    )


# ============================================================
# 3. E-MAIL DE RESET DE SENHA
# ============================================================

def enviar_email_reset_senha(usuario, token):
    """
    Envia e-mail com link para redefinir senha.
    
    Args:
        usuario: instância de Usuario
        token: str (token_reset gerado)
    
    Returns:
        dict: resultado do envio
    """
    valido, erro = validar_email(usuario.email)
    if not valido:
        print(f"⚠️ E-mail inválido: {erro}")
        return {'sucesso': False, 'erro': erro, 'destinatarios': []}
    
    link = url_for('auth.resetar_senha', token=token, _external=True)
    
    corpo = f"""
    <p style="margin: 0 0 15px 0; font-size: 15px;">
        Recebemos uma solicitação para redefinir a senha da sua conta. 
        Se foi você, clique no botão abaixo:
    </p>
    
    {_botao_html('🔐 Redefinir minha senha', link, '#2563eb')}
    
    {_info_box('''
        <p style="margin: 0; font-size: 13px;">
            <strong>⏱️ Este link expira em 1 hora.</strong><br>
            Se você não solicitou a redefinição, ignore este e-mail — 
            sua senha permanecerá a mesma.
        </p>
    ''', '#fee2e2', '#dc2626')}
    
    {_link_texto(link)}
    """
    
    html = _html_base(
        titulo="Redefinir senha",
        saudacao=f"Olá, <strong>{usuario.nome}</strong>!",
        corpo_html=corpo,
        cor_cabecalho='#2563eb'
    )
    
    return _enviar_email_generico(
        destinatarios=usuario.email,
        assunto="Redefinir senha — PTBDSWS",
        html=html,
        texto_curto=f"Redefinição de senha para {usuario.email}"
    )


# ============================================================
# 4. E-MAIL DE CONFIRMAÇÃO DE NOVO E-MAIL (troca de endereço)
# ============================================================

def enviar_email_confirmacao_novo_email(usuario, novo_email, token):
    """
    Envia e-mail de confirmação para o NOVO endereço de e-mail.
    
    Args:
        usuario: instância de Usuario (dados atuais)
        novo_email: str (endereço que será confirmado)
        token: str (token gerado para a troca)
    
    Returns:
        dict: resultado do envio
    """
    valido, erro = validar_email(novo_email)
    if not valido:
        print(f"⚠️ Novo e-mail inválido: {erro}")
        return {'sucesso': False, 'erro': erro, 'destinatarios': []}
    
    link = url_for('auth.confirmar_novo_email', token=token, _external=True)
    
    corpo = f"""
    <p style="margin: 0 0 15px 0; font-size: 15px;">
        Você solicitou a alteração do seu e-mail de acesso. 
        Clique no botão abaixo para confirmar o novo endereço:
    </p>
    
    {_botao_html('✉️ Confirmar novo e-mail', link, '#7c3aed')}
    
    {_info_box(f'''
        <p style="margin: 5px 0; font-size: 13px;">
            <strong>E-mail atual:</strong> {usuario.email}<br>
            <strong>Novo e-mail:</strong> {novo_email}
        </p>
    ''', '#ede9fe', '#7c3aed')}
    
    {_info_box('''
        <p style="margin: 0; font-size: 13px;">
            <strong>⚠️ Importante:</strong> enquanto não confirmar, 
            o e-mail antigo continua sendo o endereço de acesso à conta.
        </p>
    ''', '#fef3c7', '#f59e0b')}
    
    {_link_texto(link)}
    """
    
    html = _html_base(
        titulo="Confirme seu novo e-mail",
        saudacao=f"Olá, <strong>{usuario.nome}</strong>!",
        corpo_html=corpo,
        cor_cabecalho='#7c3aed'
    )
    
    return _enviar_email_generico(
        destinatarios=novo_email,
        assunto="Confirme seu novo e-mail — PTBDSWS",
        html=html,
        texto_curto=f"Confirmação de troca de e-mail: {usuario.email} → {novo_email}"
    )


# ============================================================
# 5. E-MAIL DE AVISO DE TROCA DE SENHA (segurança)
# ============================================================

def enviar_email_aviso_senha_alterada(usuario):
    """
    Envia e-mail de aviso após uma troca de senha bem-sucedida.
    Boa prática de segurança: informa ao usuário caso não tenha sido ele.
    
    Args:
        usuario: instância de Usuario
    
    Returns:
        dict: resultado do envio
    """
    valido, erro = validar_email(usuario.email)
    if not valido:
        print(f"⚠️ E-mail inválido: {erro}")
        return {'sucesso': False, 'erro': erro, 'destinatarios': []}
    
    corpo = f"""
    <p style="margin: 0 0 15px 0; font-size: 15px;">
        Sua senha foi alterada com sucesso em 
        <strong>{datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</strong>.
    </p>
    
    {_info_box('''
        <p style="margin: 0; font-size: 13px;">
            <strong>🔒 Se não foi você:</strong> sua conta pode ter sido comprometida. 
            Solicite imediatamente a redefinição de senha na tela de login 
            ("Esqueci minha senha") e entre em contato com o suporte.
        </p>
    ''', '#fee2e2', '#dc2626')}
    """
    
    html = _html_base(
        titulo="Senha alterada",
        saudacao=f"Olá, <strong>{usuario.nome}</strong>!",
        corpo_html=corpo,
        cor_cabecalho='#16a34a'
    )
    
    return _enviar_email_generico(
        destinatarios=usuario.email,
        assunto="Sua senha foi alterada — PTBDSWS",
        html=html,
        texto_curto=f"Aviso de alteração de senha para {usuario.email}"
    )
