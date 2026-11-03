"""
Serviço de validações reutilizáveis.
Centraliza regras de validação de campos.
"""
import re


def validar_username(username):
    """
    Valida o formato do nome de usuário.
    
    Regras:
    - 3 a 30 caracteres
    - Apenas letras minúsculas, números e underscore (_)
    - Deve começar com letra
    - Não pode ser palavra reservada
    
    Returns:
        tuple: (valido: bool, erro: str|None)
    """
    if not username:
        return False, 'Nome de usuário é obrigatório.'
    
    username = username.strip().lower()
    
    if len(username) < 3 or len(username) > 30:
        return False, 'Nome de usuário deve ter entre 3 e 30 caracteres.'
    
    if not re.match(r'^[a-z][a-z0-9_]*$', username):
        return False, 'Use apenas letras minúsculas, números e underscore (_). Deve começar com letra.'
    
    reservados = ['admin', 'root', 'sistema', 'suporte', 'moderador', 'administrador']
    if username in reservados:
        return False, 'Este nome de usuário é reservado.'
    
    return True, None


def validar_email(email):
    """Valida formato básico de e-mail."""
    if not email:
        return False, 'E-mail é obrigatório.'
    
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email.strip()):
        return False, 'E-mail inválido.'
    
    return True, None


def validar_senha(senha):
    """
    Valida a força da senha.
    
    Regras:
    - Mínimo 8 caracteres
    - Pelo menos uma letra e um número
    """
    if not senha:
        return False, 'Senha é obrigatória.'
    
    if len(senha) < 8:
        return False, 'Senha deve ter pelo menos 8 caracteres.'
    
    if not re.search(r'[a-zA-Z]', senha):
        return False, 'Senha deve conter pelo menos uma letra.'
    
    if not re.search(r'[0-9]', senha):
        return False, 'Senha deve conter pelo menos um número.'
    
    return True, None


def validar_nome(nome):
    """Valida o nome completo."""
    if not nome or len(nome.strip()) < 3:
        return False, 'Nome deve ter pelo menos 3 caracteres.'
    
    return True, None
