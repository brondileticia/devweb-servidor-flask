"""
Ponto de entrada da aplicação (uso LOCAL).
Execute com: python run.py

No PythonAnywhere quem chama create_app() é o arquivo WSGI, então este
arquivo (e os dados de exemplo abaixo) não rodam em produção.
"""
from app import create_app, db
from app.models import Usuario, EmailEnviado

app = create_app()


def criar_dados_iniciais():
    """
    Popula um banco VAZIO com exemplos dos três tipos de registro:
      - conta confirmada ....... pode logar e ver tudo
      - conta NÃO confirmada ... pode logar, mas só vê o aviso
      - registro sem conta ..... criado pelo painel Banco de Dados (só nome/função)
    """
    john = Usuario('John Smith', email='john@exemplo.com', username='john',
                   password='senha1234', funcao='Administrator')
    john.email_confirmado = True
    john.token_confirmacao = None

    susan = Usuario('Susan Lee', email='susan@exemplo.com', username='susan',
                    password='senha1234', funcao='User')  # fica pendente

    david = Usuario('David', funcao='User')
    professor = Usuario('Professor Fabio Teixeira', funcao='User')

    db.session.add_all([john, susan, david, professor])
    db.session.commit()
    print('✅ Dados iniciais criados!')
    print('   john  / senha1234 → confirmado (vê a relação)')
    print('   susan / senha1234 → NÃO confirmado (vê o aviso)')


with app.app_context():
    db.create_all()
    print('✅ Tabelas criadas/verificadas!')

    if Usuario.query.count() == 0:
        criar_dados_iniciais()

    print(f'📊 Total de usuários: {Usuario.query.count()}')
    print(f'📧 Total de e-mails: {EmailEnviado.query.count()}')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
