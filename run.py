"""
Ponto de entrada da aplicação.
Execute com: python run.py
"""
from app import create_app, db
from app.models import Usuario, EmailEnviado

app = create_app()

# Cria as tabelas e usuários iniciais no contexto da app
with app.app_context():
    db.create_all()
    print("✅ Tabelas criadas/verificadas!")
    
    if Usuario.query.count() == 0:
        from app.models import Usuario
        usuarios_iniciais = [
            Usuario("john", "Administrator"),
            Usuario("susan", "User"),
            Usuario("david", "User"),
            Usuario("Professor Fabio Teixeira", "User")
        ]
        for u in usuarios_iniciais:
            db.session.add(u)
        db.session.commit()
        print("✅ Usuários iniciais criados!")
    
    print(f"📊 Total de usuários: {Usuario.query.count()}")
    print(f"📧 Total de e-mails: {EmailEnviado.query.count()}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
