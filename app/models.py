"""
Modelos do banco de dados.
"""
from datetime import datetime
from app import db


class Usuario(db.Model):
    """Representa um usuário do sistema."""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, index=True)
    funcao = db.Column(db.String(50), nullable=False, default='User')
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    atualizado_em = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, nome, funcao='User'):
        self.nome = nome.strip()
        self.funcao = funcao.strip()
    
    def __repr__(self):
        return f'<Usuario {self.nome} - {self.funcao}>'
    
    def salvar(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar: {e}")
            return False
    
    def atualizar(self, novo_nome=None, nova_funcao=None):
        try:
            if novo_nome:
                self.nome = novo_nome.strip()
            if nova_funcao:
                self.funcao = nova_funcao.strip()
            self.atualizado_em = datetime.utcnow()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def deletar(self):
        try:
            db.session.delete(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def promover(self):
        ciclo = {'User': 'Moderator', 'Moderator': 'Administrator', 'Administrator': 'Administrator'}
        self.funcao = ciclo.get(self.funcao, 'User')
        db.session.commit()
        return True
    
    def rebaixar(self):
        ciclo = {'Administrator': 'Moderator', 'Moderator': 'User', 'User': 'User'}
        self.funcao = ciclo.get(self.funcao, 'User')
        db.session.commit()
        return True
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'funcao': self.funcao,
            'criado_em': self.criado_em.isoformat() if self.criado_em else None
        }


class EmailEnviado(db.Model):
    """Registra os e-mails enviados pelo sistema."""
    __tablename__ = 'emails_enviados'
    
    id = db.Column(db.Integer, primary_key=True)
    remetente = db.Column(db.String(200), nullable=False)
    destinatarios = db.Column(db.Text, nullable=False)
    assunto = db.Column(db.String(300), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    enviado_em = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    sucesso = db.Column(db.Boolean, default=True)
    
    def __init__(self, remetente, destinatarios, assunto, texto, sucesso=True):
        self.remetente = remetente
        self.destinatarios = destinatarios
        self.assunto = assunto
        self.texto = texto
        self.sucesso = sucesso
    
    def __repr__(self):
        return f'<EmailEnviado {self.assunto}>'
    
    def salvar(self):
        try:
            db.session.add(self)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao salvar e-mail: {e}")
            return False
    
    def to_dict(self):
        return {
            'id': self.id,
            'remetente': self.remetente,
            'destinatarios': self.destinatarios,
            'assunto': self.assunto,
            'texto': self.texto,
            'enviado_em': self.enviado_em.isoformat() if self.enviado_em else None,
            'sucesso': self.sucesso
        }
