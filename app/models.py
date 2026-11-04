from datetime import datetime, timedelta
import secrets

from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)

    # Opcionais: usuários criados pelo painel "Banco de Dados" só têm nome e função
    # e não fazem login. Usuários criados pelo /cadastro têm todos os campos.
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    username = db.Column(db.String(50), unique=True, nullable=True, index=True)
    password_hash = db.Column(db.String(256), nullable=True)

    funcao = db.Column(db.String(50), nullable=False, default='User')

    # Controle de confirmação de e-mail
    email_confirmado = db.Column(db.Boolean, default=False)
    token_confirmacao = db.Column(db.String(100), nullable=True)

    # Controle de reset de senha
    token_reset = db.Column(db.String(100), nullable=True)
    token_reset_expira = db.Column(db.DateTime, nullable=True)

    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, nome, email=None, username=None, password=None, funcao='User'):
        self.nome = nome.strip()
        self.email = email.strip().lower() if email else None
        self.username = username.strip().lower() if username else None
        self.funcao = funcao
        if password:
            self.set_password(password)
            self.gerar_token_confirmacao()

    @property
    def pode_logar(self):
        return bool(self.password_hash)

    # ============ SENHA ============
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)

    # ============ CONFIRMAÇÃO DE E-MAIL ============
    def gerar_token_confirmacao(self):
        self.token_confirmacao = secrets.token_urlsafe(32)
        return self.token_confirmacao

    def confirmar_email(self, token):
        if self.token_confirmacao and self.token_confirmacao == token:
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
        return bool(
            self.token_reset
            and self.token_reset == token
            and self.token_reset_expira
            and datetime.utcnow() < self.token_reset_expira
        )

    def resetar_senha(self, nova_senha):
        self.set_password(nova_senha)
        self.token_reset = None
        self.token_reset_expira = None
        db.session.commit()

    # ============ HIERARQUIA DE FUNÇÕES ============
    # FUNCOES = ['User', 'Moderator', 'Administrator'] (do menor para o maior)
    def promover(self):
        funcoes = current_app.config['FUNCOES']
        i = funcoes.index(self.funcao) if self.funcao in funcoes else 0
        if i < len(funcoes) - 1:
            self.funcao = funcoes[i + 1]
            db.session.commit()
            return True
        return False

    def rebaixar(self):
        funcoes = current_app.config['FUNCOES']
        i = funcoes.index(self.funcao) if self.funcao in funcoes else 0
        if i > 0:
            self.funcao = funcoes[i - 1]
            db.session.commit()
            return True
        return False

    def __repr__(self):
        return f'<Usuario {self.nome} ({self.funcao})>'


class EmailEnviado(db.Model):
    __tablename__ = 'emails_enviados'

    id = db.Column(db.Integer, primary_key=True)
    remetente = db.Column(db.String(200), nullable=False)
    destinatarios = db.Column(db.Text, nullable=False)
    assunto = db.Column(db.String(200), nullable=False)
    texto = db.Column(db.Text, nullable=True)
    sucesso = db.Column(db.Boolean, default=False)
    enviado_em = db.Column(db.DateTime, default=datetime.utcnow)

    def salvar(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'<EmailEnviado {self.assunto}>'


@login_manager.user_loader
def carregar_usuario(user_id):
    return db.session.get(Usuario, int(user_id))
