"""
Factory da aplicação Flask.
Registra as extensões e os blueprints.
"""
import flask
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from config import Config

# Extensões (instanciadas sem app, para permitir factory pattern)
db = SQLAlchemy()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config_class=Config):
    """Cria e configura a aplicação Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializa extensões
    db.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    
    # Registra blueprints
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from app.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/banco-dados')
    
    from app.emails import bp as emails_bp
    app.register_blueprint(emails_bp)
    
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    # Context processor global
    @app.context_processor
    def inject_globals():
        from app.models import Usuario, EmailEnviado
        try:
            total_usuarios = Usuario.query.count()
            total_emails = EmailEnviado.query.count()
        except Exception:
            total_usuarios = 0
            total_emails = 0
        
        return {
            'flask_version': flask.__version__,
            'aluno': {
                'nome': app.config['ALUNO_NOME'],
                'prontuario': app.config['ALUNO_PRONTUARIO'],
                'instituicao': app.config['ALUNO_INSTITUICAO'],
                'email_institucional': app.config['EMAIL_INSTITUCIONAL'],
            },
            'ano_atual': __import__('datetime').datetime.now().year,
            'app_name': 'Avaliação contínua: Semana 12',
            'funcoes': app.config['FUNCOES'],
            'icones_funcoes': app.config['ICONES_FUNCOES'],
            'hierarquia_funcoes': app.config['HIERARQUIA_FUNCOES'],
            'email_professor': app.config['EMAIL_PROFESSOR'],
            'email_institucional': app.config['EMAIL_INSTITUCIONAL'],
            'total_usuarios_badge': total_usuarios,
            'total_emails_badge': total_emails,
        }
    
    # Handlers de erro
    @app.errorhandler(404)
    def page_not_found(e):
        return flask.render_template('404.html', titulo='Página não encontrada'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return flask.render_template('500.html', titulo='Erro do servidor'), 500
    
    return app
