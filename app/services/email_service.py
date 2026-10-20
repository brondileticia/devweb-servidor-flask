"""
Serviço responsável pelo envio e persistência de e-mails.
"""
from datetime import datetime
import requests
from flask import current_app

from app import db
from app.models import EmailEnviado


def enviar_email_novo_usuario(nome_usuario, funcao, enviar_para_professor=False):
    """
    Envia e-mail via Mailgun e persiste no banco.
    
    Args:
        nome_usuario: Nome do usuário recém-cadastrado
        funcao: Função do usuário
        enviar_para_professor: Se True, envia também para flaskaulasweb@zohomail.com
    
    Returns:
        bool: True se enviado, False caso contrário
    """
    api_key = current_app.config['MAILGUN_API_KEY']
    domain = current_app.config['MAILGUN_DOMAIN']
    email_institucional = current_app.config['EMAIL_INSTITUCIONAL']
    email_professor = current_app.config['EMAIL_PROFESSOR']
    aluno_nome = current_app.config['ALUNO_NOME']
    aluno_prontuario = current_app.config['ALUNO_PRONTUARIO']
    
    if not api_key:
        print("⚠️ API key do Mailgun não configurada.")
        return False
    
    from_addr = f"Flasky <postmaster@{domain}>"
    url = f"https://api.mailgun.net/v3/{domain}/messages"
    
    # Destinatários
    destinatarios = [email_institucional]
    if enviar_para_professor:
        destinatarios.append(email_professor)
    
    # Assunto e texto
    assunto = f"[Flasky] Novo usuário"
    texto_curto = f"Novo usuário cadastrado: {nome_usuario}"
    
    # Aviso opcional no HTML
    aviso_professor = ""
    if enviar_para_professor:
        aviso_professor = f"""
        <div style="background-color: #d4edda; color: #155724; padding: 10px; border-radius: 5px; margin-top: 15px;">
            ✉️ Este e-mail também foi enviado para <strong>{email_professor}</strong>
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
                {aviso_professor}
            </div>
        </div>
    </body>
    </html>
    """
    
    sucesso = False
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
            print(f"❌ Erro Mailgun: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
    
    # Persiste SEMPRE (sucesso ou falha)
    registro = EmailEnviado(
        remetente=from_addr,
        destinatarios=str(destinatarios),
        assunto=assunto,
        texto=texto_curto,
        sucesso=sucesso
    )
    registro.salvar()
    
    return sucesso
