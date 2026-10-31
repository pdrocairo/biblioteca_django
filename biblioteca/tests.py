from datetime import date
from unittest import mock

from django.contrib.auth.models import User
from django.db.models import ProtectedError
from rest_framework import status
from rest_framework.test import APITestCase

from biblioteca import services
from biblioteca.models import (
    Autor, Categoria, Editora, Emprestimo, Exemplar, Livro, Usuario,
)

SENHA = 'senha-de-teste-123'
URL_EMPRESTIMO = '/api/emprestimos/registrar_emprestimo/'
URL_DEVOLUCAO = '/api/emprestimos/registrar_devolucoes/'


def criar_usuario(username, perfil):
    user = User.objects.create_user(username=username, email=f'{username}@teste.com', password=SENHA)
    return Usuario.objects.create(user=user, nome=username, email=user.email, perfil=perfil)


class BaseTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.bibliotecario = criar_usuario('bibliotecario', Usuario.PERFIL_BIBLIOTECARIO)
        cls.leitor = criar_usuario('leitor', Usuario.PERFIL_LEITOR)
        cls.outro_leitor = criar_usuario('outro', Usuario.PERFIL_LEITOR)

        livro_base = dict(
            categoria=Categoria.objects.create(nome='Romance'),
            autor=Autor.objects.create(nome='Autor', nacionalidade='BR'),
            editora=Editora.objects.create(nome='Editora', cidade='Rio'),
        )
        cls.livro = Livro.objects.create(titulo='Dom Casmurro', **livro_base)
        cls.livro_sem_exemplar = Livro.objects.create(titulo='Sem estoque', **livro_base)
        cls.exemplar = Exemplar.objects.create(livro=cls.livro, codigo_tombo='DC-001')

    def autenticar(self, usuario):
        self.client.force_authenticate(usuario.user)

    def emprestar(self, usuario_id, livro_id):
        return self.client.post(
            URL_EMPRESTIMO, {'id_usuario': usuario_id, 'id_livro': livro_id}, format='json')

    def devolver(self, usuario_id, exemplar_id):
        return self.client.patch(
            URL_DEVOLUCAO, {'id_usuario': usuario_id, 'id_exemplar': exemplar_id}, format='json')


class EmprestimoTests(BaseTestCase):
    def setUp(self):
        self.autenticar(self.bibliotecario)

    def test_emprestimo_feito(self):
        resposta = self.emprestar(self.leitor.id, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.exemplar.refresh_from_db()
        self.assertFalse(self.exemplar.disponivel)
        emprestimo = Emprestimo.objects.get()
        self.assertEqual((emprestimo.usuario, emprestimo.exemplar), (self.leitor, self.exemplar))
        self.assertTrue(emprestimo.ativo)
        self.assertIsNone(emprestimo.data_devolucao)

    def test_usuario_com_emprestimo_ativo_e_bloqueado(self):
        Exemplar.objects.create(livro=self.livro, codigo_tombo='DC-002')
        self.emprestar(self.leitor.id, self.livro.id)

        resposta = self.emprestar(self.leitor.id, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(Emprestimo.objects.count(), 1)
        self.assertEqual(Exemplar.objects.filter(disponivel=False).count(), 1)

    def test_livro_sem_exemplar_disponivel(self):
        resposta = self.emprestar(self.leitor.id, self.livro_sem_exemplar.id)

        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)
        self.assertFalse(Emprestimo.objects.exists())

    def test_ultimo_exemplar_emprestado_bloqueia_o_proximo_leitor(self):
        self.emprestar(self.leitor.id, self.livro.id)

        resposta = self.emprestar(self.outro_leitor.id, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)

    def test_usuario_inexistente_nao_deixa_exemplar_travado(self):
        resposta = self.emprestar(999, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)
        self.exemplar.refresh_from_db()
        self.assertTrue(self.exemplar.disponivel)

    def test_livro_inexistente(self):
        resposta = self.emprestar(self.leitor.id, 999)

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_id_fora_do_intervalo_do_banco_retorna_400(self):
        resposta = self.emprestar(20252014040026, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('erro', resposta.json())
        self.exemplar.refresh_from_db()
        self.assertTrue(self.exemplar.disponivel)

    def test_campos_obrigatorios(self):
        resposta = self.client.post(URL_EMPRESTIMO, {}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_falha_ao_criar_emprestimo_desfaz_a_troca_de_disponibilidade(self):
        with mock.patch.object(Emprestimo.objects, 'create', side_effect=RuntimeError('falha')):
            with self.assertRaises(RuntimeError):
                services.registrar_emprestimo(self.leitor.id, self.livro.id)

        self.exemplar.refresh_from_db()
        self.assertTrue(self.exemplar.disponivel)


class DevolucaoTests(BaseTestCase):
    def setUp(self):
        self.autenticar(self.bibliotecario)

    def test_devolucao_feita(self):
        self.emprestar(self.leitor.id, self.livro.id)

        resposta = self.devolver(self.leitor.id, self.exemplar.id)

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.exemplar.refresh_from_db()
        self.assertTrue(self.exemplar.disponivel)
        emprestimo = Emprestimo.objects.get()
        self.assertFalse(emprestimo.ativo)
        self.assertIsNotNone(emprestimo.data_devolucao)
        self.assertIsInstance(emprestimo.data_devolucao, date)

    def test_devolucao_de_exemplar_que_nao_esta_emprestado(self):
        resposta = self.devolver(self.leitor.id, self.exemplar.id)

        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)

    def test_devolucao_por_usuario_que_nao_pegou_o_exemplar(self):
        self.emprestar(self.leitor.id, self.livro.id)

        resposta = self.devolver(self.outro_leitor.id, self.exemplar.id)

        self.assertEqual(resposta.status_code, status.HTTP_409_CONFLICT)
        self.exemplar.refresh_from_db()
        self.assertFalse(self.exemplar.disponivel)

    def test_exemplar_inexistente(self):
        resposta = self.devolver(self.leitor.id, 999)

        self.assertEqual(resposta.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_pode_emprestar_de_novo_apos_devolver(self):
        self.emprestar(self.leitor.id, self.livro.id)
        self.devolver(self.leitor.id, self.exemplar.id)

        resposta = self.emprestar(self.leitor.id, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)


class PermissaoTests(BaseTestCase):
    def test_acesso_sem_token_recebe_401(self):
        urls = ['/api/livros/', '/api/exemplares/', '/api/usuarios/', '/api/emprestimos/']
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            self.emprestar(self.leitor.id, self.livro.id).status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            self.devolver(self.leitor.id, self.exemplar.id).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_leitor_nao_registra_emprestimo_nem_devolucao(self):
        self.autenticar(self.leitor)

        self.assertEqual(
            self.emprestar(self.leitor.id, self.livro.id).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.devolver(self.leitor.id, self.exemplar.id).status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Emprestimo.objects.exists())

    def test_leitor_consulta_o_catalogo(self):
        self.autenticar(self.leitor)

        self.assertEqual(self.client.get('/api/livros/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/exemplares/').status_code, status.HTTP_200_OK)

    def test_user_sem_usuario_vinculado_e_negado(self):
        sem_perfil = User.objects.create_user(username='sem_perfil', password=SENHA)
        self.client.force_authenticate(sem_perfil)

        resposta = self.emprestar(self.leitor.id, self.livro.id)

        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)


class UsuarioApiTests(BaseTestCase):
    def test_resposta_nao_expoe_senha(self):
        self.autenticar(self.bibliotecario)

        resposta = self.client.get('/api/usuarios/')

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        for usuario in resposta.json():
            self.assertEqual(set(usuario), {'id', 'nome', 'email', 'perfil', 'username'})

    def test_bibliotecario_cria_usuario_com_senha_em_hash(self):
        self.autenticar(self.bibliotecario)

        resposta = self.client.post('/api/usuarios/', {
            'nome': 'Novo', 'email': 'novo@teste.com', 'perfil': 'leitor',
            'username': 'novo', 'password': SENHA,
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', resposta.json())
        user = User.objects.get(username='novo')
        self.assertNotEqual(user.password, SENHA)
        self.assertTrue(user.check_password(SENHA))
        self.assertEqual(user.usuario.nome, 'Novo')

    def test_senha_fraca_e_rejeitada(self):
        self.autenticar(self.bibliotecario)

        resposta = self.client.post('/api/usuarios/', {
            'nome': 'Novo', 'email': 'novo@teste.com', 'username': 'novo', 'password': '123',
        }, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(username='novo').exists())

    def test_leitor_nao_gerencia_usuarios(self):
        self.autenticar(self.leitor)

        self.assertEqual(self.client.get('/api/usuarios/').status_code, status.HTTP_403_FORBIDDEN)
        resposta = self.client.post('/api/usuarios/', {
            'nome': 'Hacker', 'email': 'h@teste.com', 'perfil': 'bibliotecario',
            'username': 'hacker', 'password': SENHA,
        }, format='json')
        self.assertEqual(resposta.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_jwt_corresponde_a_um_usuario(self):
        resposta = self.client.post(
            '/api/token/', {'username': 'bibliotecario', 'password': SENHA}, format='json')

        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertIn('access', resposta.json())
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resposta.json()['access']}")
        self.assertEqual(self.emprestar(self.leitor.id, self.livro.id).status_code, status.HTTP_201_CREATED)


class ProtecaoDoHistoricoTests(BaseTestCase):
    def setUp(self):
        self.autenticar(self.bibliotecario)
        self.emprestar(self.leitor.id, self.livro.id)

    def test_nao_apaga_usuario_com_emprestimos(self):
        with self.assertRaises(ProtectedError):
            self.leitor.delete()
        self.assertEqual(Emprestimo.objects.count(), 1)

    def test_nao_apaga_exemplar_com_emprestimos(self):
        with self.assertRaises(ProtectedError):
            self.exemplar.delete()
        self.assertEqual(Emprestimo.objects.count(), 1)
