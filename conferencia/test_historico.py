from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Devolucao, Produto, Recebimento


class HistoricoTests(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="demo.operador", password="senha-de-teste-123"
        )
        self.produto = Produto.objects.create(
            codigo_sku="AP-0012", descricao="Botão do rádio (exemplo)"
        )

    def entrar(self):
        self.client.login(username="demo.operador", password="senha-de-teste-123")

    def test_exige_login(self):
        resposta = self.client.get(reverse("historico"))
        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("login"), resposta["Location"])

    def test_sem_conferencias_mostra_mensagem(self):
        self.entrar()
        resposta = self.client.get(reverse("historico"))
        self.assertContains(resposta, "Nenhuma conferência feita ainda")

    def test_lista_recebimento_e_devolucao_conferidos(self):
        recebimento = Recebimento.objects.create(
            produto=self.produto, fornecedor="Fornecedor Exemplo", quantidade_comprada=100
        )
        recebimento.conferir(self.usuario, 98, "ok")
        devolucao = Devolucao.objects.create(produto=self.produto, quantidade=1)
        devolucao.conferir(self.usuario, "danificada", "descarte")
        self.entrar()
        resposta = self.client.get(reverse("historico"))
        self.assertContains(resposta, "Divergência de 2 unidade(s)")
        self.assertContains(resposta, "Corrigir o saldo de 100 para 98")
        self.assertContains(resposta, "Danificada, destino Descarte")
        self.assertContains(resposta, "Dar saída por descarte")
        self.assertContains(resposta, "demo.operador")

    def test_nao_lista_itens_pendentes(self):
        Recebimento.objects.create(
            produto=self.produto, fornecedor="Fornecedor Exemplo", quantidade_comprada=10
        )
        Devolucao.objects.create(produto=self.produto, quantidade=1)
        self.entrar()
        resposta = self.client.get(reverse("historico"))
        self.assertContains(resposta, "Nenhuma conferência feita ainda")

    def test_mais_recente_aparece_primeiro(self):
        antigo = Devolucao.objects.create(produto=self.produto, quantidade=1, numero_pedido="A")
        antigo.conferir(self.usuario, "ok", "estoque")
        recente = Devolucao.objects.create(produto=self.produto, quantidade=1, numero_pedido="B")
        recente.conferir(self.usuario, "danificada", "reparo")
        self.entrar()
        itens = self.client.get(reverse("historico")).context["itens"]
        self.assertEqual(itens[0]["resultado"], "Danificada, destino Reparo")
        self.assertEqual(itens[1]["resultado"], "Ok, destino Estoque")

    def test_menu_inicial_tem_botao_historico(self):
        self.entrar()
        resposta = self.client.get(reverse("inicio"))
        self.assertContains(resposta, reverse("historico"))


class ModoEscuroTests(TestCase):
    def test_botao_de_modo_escuro_esta_em_todas_as_telas(self):
        resposta = self.client.get(reverse("login"))
        self.assertContains(resposta, 'id="alternar-tema"')
        self.assertContains(resposta, "Modo escuro")
