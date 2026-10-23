"""
Serviço responsável pelo envio e persistência de e-mails.
Semana 13: e-mail adicional + checkbox opcional para o professor.
"""
from datetime import datetime
import re
import requests
from flask import current_app

from app import db
from app.models import EmailEnviado


def validar_email(email):
    """Valida formato básico de e-mail."""
    if not email:
        return False
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(padrao, email.strip()) is not None


def enviar_email_novo_usuario(nome_usuario, funcao, email_adicional=None, enviar_para_professor=False):
    """
    Envia e-mail via Mailgun e persiste no banco.
    
    Semana 13 (mantendo opção da Semana 11):
    - SEMPRE envia para o e-mail institucional
    - Envia para o professor SOMENTE se enviar_para_professor=True
    - OPCIONALMENTE envia para um e-mail adicional digitado no formulário
    
    Args:
        nome_usuario: Nome do usuário recém-cadastrado
        funcao: Função do usuário
        email_adicional: E-mail extra digitado pelo usuário (opcional)
        enviar_para_professor: Se True, envia também para flaskaulasweb@zohomail.com
    
    Returns:
        dict: {
            'sucesso': bool,
            'destinatarios': list,
            'erro': str or None,
            'email_adicional_valido': bool,
            'enviado_professor': bool,
        }
    """
    api_key = current_app.config['MAILGUN_API_KEY']
    domain = current_app.config['MAILGUN_DOMAIN']
    email_institucional = current_app.config['EMAIL_INSTITUCIONAL']
    email_professor = current_app.config['EMAIL_PROFESSOR']
    aluno_nome = current_app.config['ALUNO_NOME']
    aluno_prontuario = current_app.config['ALUNO_PRONTUARIO']
    
    if not api_key:
        print("⚠️ API key do Mailgun não configurada.")
        return {
            'sucesso': False,
            'destinatarios': [],
            'erro': 'API key não configurada',
            'email_adicional_valido': False,
            'enviado_professor': False,
        }
    
    from_addr = f"Flasky <postmaster@{domain}>"
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    # ============ DESTINATÁRIOS ============
    # Institucional é SEMPRE destinatário
    destinatarios = [email_institucional]
    
    # Professor é OPCIONAL (checkbox)
    if enviar_para_professor:
        destinatarios.append(email_professor)
    
    # E-mail adicional é OPCIONAL (campo de texto)
    email_adicional_valido = False
    if email_adicional:
        email_adicional = email_adicional.strip()
        if validar_email(email_adicional) and email_adicional not in destinatarios:
            destinatarios.append(email_adicional)
            email_adicional_valido = True
    
    # ============ ASSUNTO E TEXTO ============
    assunto = "[Flasky] Novo usuário"
    texto_curto = f"Novo usuário cadastrado: {nome_usuario}"
    
    # Blocos HTML de aviso
    bloco_professor = ""
    if enviar_para_professor:
        bloco_professor = f"""
        <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-top: 15px;">
            ✉️ Este e-mail também foi enviado para o professor: <strong>{email_professor}</strong>
        </div>
        """
    
    bloco_adicional = ""
    if email_adicional_valido:
        bloco_adicional = f"""
        <div style="background-color: #d1ecf1; color: #0c5460; padding: 10px; border-radius: 5px; margin-top: 15px;">
            ✉️ Este e-mail também foi enviado para: <strong>{email_adicional}</strong>
        </div>
        """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"></head>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 5px;">
            <div style="background-color: #337ab7; color: white; padding: 20px;">
                <h2 style="margin: 0;">📧 Novo Usuário Cadastrado</h2>
            </div>
            <div style="padding: 20px; background-color: #f9f9f9;">
                <p>Um novo usuário foi cadastrado no sistema!</p>
                <div style="background-color: white; padding: 15px; border-left: 4px solid #337ab7;">
                    <p><strong>Prontuário do aluno:</strong> {aluno_prontuario}</p>
                    <p><strong>Nome do aluno:</strong> {aluno_nome}</p>
                    <p><strong>Usuário cadastrado:</strong> {nome_usuario}</p>
                    <p><strong>Função:</strong> {funcao}</p>
                    <p><strong>Data e hora:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
                </div>
                {bloco_professor}
                {bloco_adicional}
                <p style="font-size: 12px; color: #777; margin-top: 20px;">
                    Este é um e-mail automático da aplicação PTBDSWS.
                </p>
            </div>
            <div style="background-color: #2c3e50; color: #bdc3c7; padding: 15px; text-align: center; font-size: 12px;">
                <p><strong>PTBDSWS</strong> - Programação em Desenvolvimento Web Servidor</p>
                <p>4º Semestre - Análise e Desenvolvimento de Sistemas</p>
                <p>IFSP - Campus Pirituba</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # ============ ENVIO ============
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
                "html": html_content
            },
            timeout=10
        )
        sucesso = response.status_code == 200
        
        if sucesso:
            print(f"✅ E-mail enviado! Para: {destinatarios}")
        else:
            erro = f"{response.status_code} - {response.text}"
            print(f"❌ Erro Mailgun: {erro}")
    except Exception as e:
        erro = str(e)
        print(f"❌ Erro ao enviar e-mail: {e}")
    
    # ============ PERSISTÊNCIA ============
    registro = EmailEnviado(
        remetente=from_addr,
        destinatarios=str(destinatarios),
        assunto=assunto,
        texto=texto_curto,
        sucesso=sucesso
    )
    registro.salvar()
    
    return {
        'sucesso': sucesso,
        'destinatarios': destinatarios,
        'erro': erro,
        'email_adicional_valido': email_adicional_valido,
        'enviado_professor': enviar_para_professor,
    }
