from datetime import datetime, timedelta
import secrets
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    funcao = db.Column(db.String(50), nullable=False, default='User')
    
    # Controle de confirmação de e-mail
    email_confirmado = db.Column(db.Boolean, default=False)
    token_confirmacao = db.Column(db.String(100), nullable=True)
    
    # Controle de reset de senha
    token_reset = db.Column(db.String(100), nullable=True)
    token_reset_expira = db.Column(db.DateTime, nullable=True)
    
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, nome, email, username, password, funcao='User'):
        self.nome = nome.strip()
        self.email = email.strip().lower()
        self.username = username.strip().lower()
        self.set_password(password)
        self.funcao = funcao
        self.gerar_token_confirmacao()
    
    # ============ SENHA ============
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # ============ CONFIRMAÇÃO DE E-MAIL ============
    def gerar_token_confirmacao(self):
        self.token_confirmacao = secrets.token_urlsafe(32)
        return self.token_confirmacao
    
    def confirmar_email(self, token):
        if self.token_confirmacao == token:
            self.email_confirmado = True
            self.token_confirmacao = None
            db.session.commit()
            return True
        return False
    
    # ============ RESET DE SENHA ============
    def gerar_token_reset(self):
        self.token_reset = secrets.token_urlsafe(32)
        self.token_reset_expira = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()
        return self.token_reset
    
    def validar_token_reset(self, token):
        if (self.token_reset == token and 
            self.token_reset_expira and 
            datetime.utcnow() < self.token_reset_expira):
            return True
        return False
    
    def resetar_senha(self, nova_senha):
        self.set_password(nova_senha)
        self.token_reset = None
        self.token_reset_expira = None
        db.session.commit()
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.email}>'
