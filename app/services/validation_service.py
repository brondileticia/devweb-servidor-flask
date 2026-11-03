"""
Serviço de validações reutilizáveis.
Centraliza todas as regras de validação de campos do sistema.

Semana 15: validação de username, e-mail, senha e nome.
"""
import re


# ============================================================
# CONSTANTES
# ============================================================

USERNAME_MIN_LEN = 3
USERNAME_MAX_LEN = 30
USERNAME_RESERVADOS = [
    'admin', 'root', 'sistema', 'suporte',
    'moderador', 'administrador', 'superuser',
    'staff', 'api', 'www', 'mail', 'ftp',
    'contato', 'ajuda', 'login', 'cadastro',
]

SENHA_MIN_LEN = 8

NOME_MIN_LEN = 3
NOME_MAX_LEN = 100

EMAIL_MAX_LEN = 120


# ============================================================
# VALIDAÇÃO DE USERNAME
# ============================================================

def validar_username(username):
    """
    Valida o formato do nome de usuário.
    
    Regras:
    - Obrigatório
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
    
    if len(username) < USERNAME_MIN_LEN:
        return False, f'Nome de usuário deve ter pelo menos {USERNAME_MIN_LEN} caracteres.'
    
    if len(username) > USERNAME_MAX_LEN:
        return False, f'Nome de usuário deve ter no máximo {USERNAME_MAX_LEN} caracteres.'
    
    if not re.match(r'^[a-z][a-z0-9_]*$', username):
        return False, (
            'Nome de usuário inválido. Use apenas letras minúsculas, '
            'números e underscore (_), começando com letra.'
        )
    
    # Verifica se termina com underscore (evita usernames estranhos)
    if username.endswith('_'):
        return False, 'Nome de usuário não pode terminar com underscore (_).'
    
    # Verifica underscores consecutivos
    if '__' in username:
        return False, 'Nome de usuário não pode ter underscores consecutivos.'
    
    if username in USERNAME_RESERVADOS:
        return False, 'Este nome de usuário é reservado pelo sistema.'
    
    return True, None


# ============================================================
# VALIDAÇÃO DE E-MAIL
# ============================================================

def validar_email(email):
    """
    Valida formato básico de e-mail.
    
    Returns:
        tuple: (valido: bool, erro: str|None)
    """
    if not email:
        return False, 'E-mail é obrigatório.'
    
    email = email.strip().lower()
    
    if len(email) > EMAIL_MAX_LEN:
        return False, f'E-mail deve ter no máximo {EMAIL_MAX_LEN} caracteres.'
    
    padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(padrao, email):
        return False, 'Formato de e-mail inválido.'
    
    # Verifica pontos consecutivos
    if '..' in email:
        return False, 'E-mail não pode ter pontos consecutivos.'
    
    # Verifica se domínio tem pelo menos um ponto
    dominio = email.split('@')[1]
    if '.' not in dominio:
        return False, 'Domínio do e-mail inválido.'
    
    return True, None


# ============================================================
# VALIDAÇÃO DE SENHA
# ============================================================

def validar_senha(senha):
    """
    Valida a força da senha.
    
    Regras:
    - Mínimo 8 caracteres
    - Pelo menos uma letra
    - Pelo menos um número
    
    Returns:
        tuple: (valido: bool, erro: str|None)
    """
    if not senha:
        return False, 'Senha é obrigatória.'
    
    if len(senha) < SENHA_MIN_LEN:
        return False, f'Senha deve ter pelo menos {SENHA_MIN_LEN} caracteres.'
    
    if not re.search(r'[a-zA-Z]', senha):
        return False, 'Senha deve conter pelo menos uma letra.'
    
    if not re.search(r'[0-9]', senha):
        return False, 'Senha deve conter pelo menos um número.'
    
    return True, None


def validar_confirmacao_senha(senha, confirmacao):
    """
    Valida se senha e confirmação são iguais.
    
    Returns:
        tuple: (valido: bool, erro: str|None)
    """
    if not confirmacao:
        return False, 'Confirmação de senha é obrigatória.'
    
    if senha != confirmacao:
        return False, 'Senhas não conferem.'
    
    return True, None


# ============================================================
# VALIDAÇÃO DE NOME
# ============================================================

def validar_nome(nome):
    """
    Valida o nome completo.
    
    Returns:
        tuple: (valido: bool, erro: str|None)
    """
    if not nome:
        return False, 'Nome é obrigatório.'
    
    nome = nome.strip()
    
    if len(nome) < NOME_MIN_LEN:
        return False, f'Nome deve ter pelo menos {NOME_MIN_LEN} caracteres.'
    
    if len(nome) > NOME_MAX_LEN:
        return False, f'Nome deve ter no máximo {NOME_MAX_LEN} caracteres.'
    
    # Deve conter pelo menos uma letra (evita "123", "   ", "***")
    if not re.search(r'[a-zA-ZÀ-ÿ]', nome):
        return False, 'Nome deve conter pelo menos uma letra.'
    
    return True, None


# ============================================================
# VALIDAÇÃO COMBINADA (para cadastro)
# ============================================================

def validar_cadastro(nome, email, username, senha, confirmacao):
    """
    Valida todos os campos do cadastro de uma vez.
    
    Returns:
        tuple: (valido: bool, erros: list[str])
    """
    erros = []
    
    valido, erro = validar_nome(nome)
    if not valido:
        erros.append(erro)
    
    valido, erro = validar_email(email)
    if not valido:
        erros.append(erro)
    
    valido, erro = validar_username(username)
    if not valido:
        erros.append(erro)
    
    valido, erro = validar_senha(senha)
    if not valido:
        erros.append(erro)
    
    valido, erro = validar_confirmacao_senha(senha, confirmacao)
    if not valido:
        erros.append(erro)
    
    return (len(erros) == 0, erros)
