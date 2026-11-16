"""
Testes da Semana 16 — controle de acesso por estado do usuário.

Rodar (na pasta do projeto, com o venv ativo):
    python -m unittest -v

O test client do Flask simula um navegador: faz GET/POST e guarda o cookie
de sessão entre as requisições, então dá para "logar" e navegar como gente.
"""
import unittest

from app import create_app, db
from app.models import Usuario
from config import TestConfig


class AcessoTestCase(unittest.TestCase):

    # ---------- preparação: roda antes de CADA teste ----------
    def setUp(self):
        self.app = create_app(TestConfig)
        self.ctx = self.app.app_context()
        self.ctx.push()
        db.create_all()

        self.john = Usuario('John Smith', email='john@exemplo.com', username='john',
                            password='senha1234', funcao='Administrator')
        self.john.email_confirmado = True
        self.susan = Usuario('Susan Lee', email='susan@exemplo.com', username='susan',
                             password='senha1234')
        db.session.add_all([self.john, self.susan, Usuario('David')])
        db.session.commit()

        self.client = self.app.test_client()

    # ---------- limpeza: roda depois de CADA teste ----------
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    # ---------- utilitários ----------
    def login(self, usuario, senha='senha1234'):
        return self.client.post('/login', data={'identificador': usuario, 'senha': senha},
                                follow_redirects=True)

    def html(self, url):
        return self.client.get(url, follow_redirects=True).get_data(as_text=True)

    # ============ 1. ANÔNIMO ============
    def test_anonimo_ve_apenas_ola_desconhecido(self):
        pagina = self.html('/')
        self.assertIn('Olá, Desconhecido!', pagina)
        self.assertNotIn('Usuários cadastrados', pagina)
        self.assertNotIn('john@exemplo.com', pagina)    # o dado nem sai do servidor
        self.assertNotIn('Banco de Dados', pagina)      # menu escondido

    def test_anonimo_e_mandado_para_o_login(self):
        for url in ['/data-hora', '/banco-dados/', '/emailsEnviados', '/identificacao', '/user/ana']:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, url)
            self.assertIn('/login', resp.headers['Location'], url)
            self.assertIn('next=', resp.headers['Location'], url)

    def test_telas_publicas_continuam_abertas(self):
        for url in ['/login', '/cadastro', '/esqueci-senha']:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_pagina_inexistente_continua_404(self):
        self.assertEqual(self.client.get('/nao-existe').status_code, 404)

    # ============ 2. LOGADO SEM CONFIRMAR ============
    def test_nao_confirmado_consegue_logar_mas_ve_aviso(self):
        pagina = self.login('susan').get_data(as_text=True)
        self.assertIn('Olá, Susan!', pagina)
        self.assertIn('não pode acessar', pagina)
        self.assertNotIn('Usuários cadastrados', pagina)
        self.assertNotIn('john@exemplo.com', pagina)

    def test_nao_confirmado_nao_acessa_outras_paginas(self):
        self.login('susan')
        for url in ['/data-hora', '/banco-dados/', '/emailsEnviados', '/alterar-senha']:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, url)
            self.assertTrue(resp.headers['Location'].endswith('/'), url)

    def test_reenviar_confirmacao_gera_token_novo(self):
        self.login('susan')
        token_antigo = self.susan.token_confirmacao
        resp = self.client.post('/reenviar-confirmacao')
        self.assertEqual(resp.status_code, 302)
        db.session.refresh(self.susan)
        self.assertNotEqual(token_antigo, self.susan.token_confirmacao)

    def test_confirmar_pelo_link_libera_o_acesso(self):
        self.login('susan')
        self.client.get(f'/confirmar/{self.susan.token_confirmacao}')
        pagina = self.html('/')
        self.assertIn('Usuários cadastrados', pagina)
        self.assertEqual(self.client.get('/data-hora').status_code, 200)

    # ============ 3. LOGADO E CONFIRMADO ============
    def test_confirmado_ve_a_relacao_completa(self):
        pagina = self.login('john').get_data(as_text=True)
        self.assertIn('Usuários cadastrados', pagina)
        for coluna in ['Nome', 'E-mail', 'Username', 'Confirmado']:
            self.assertIn(f'<th', pagina)
            self.assertIn(coluna, pagina)
        self.assertIn('susan@exemplo.com', pagina)
        self.assertIn('john', pagina)
        self.assertIn('David', pagina)

    def test_confirmado_acessa_todas_as_atividades(self):
        from app.main.atividades import ATIVIDADES
        self.login('john')
        with self.app.test_request_context():
            from flask import url_for
            urls = [url_for(a['endpoint']) for a in ATIVIDADES]
        for url in urls:
            self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_home_nao_mostra_mais_a_tag_de_aula(self):
        pagina = self.login('john').get_data(as_text=True)
        self.assertNotIn('Aula 040', pagina)
        self.assertNotIn('Aula 050.B', pagina)

    def test_logout_volta_a_ser_desconhecido(self):
        self.login('john')
        pagina = self.html('/logout')
        self.assertIn('Olá, Desconhecido!', pagina)


if __name__ == '__main__':
    unittest.main()
