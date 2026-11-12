from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Devolucao, Produto, Recebimento


class TelasBase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="demo.operador", password="senha-de-teste-123"
        )
        self.produto = Produto.objects.create(
            codigo_sku="AP-0012", descricao="Botão do rádio (exemplo)"
        )
        self.devolucao = Devolucao.objects.create(
            produto=self.produto, canal_origem="Mercado Livre",
            numero_pedido="0000-DEMO", quantidade=1,
        )

    def entrar(self):
        self.client.login(username="demo.operador", password="senha-de-teste-123")


class AcessoTests(TelasBase):
    def test_telas_exigem_login(self):
        urls = [
            reverse("inicio"),
            reverse("fila_devolucoes"),
            reverse("registrar_recebimento"),
            reverse("conferir_devolucao", args=[self.devolucao.pk]),
        ]
        for url in urls:
            resposta = self.client.get(url)
            self.assertEqual(resposta.status_code, 302, url)
            self.assertIn(reverse("login"), resposta["Location"])

    def test_login_com_senha_correta_leva_ao_menu(self):
        resposta = self.client.post(
            reverse("login"),
            {"username": "demo.operador", "password": "senha-de-teste-123"},
        )
        self.assertRedirects(resposta, reverse("inicio"))

    def test_login_com_senha_errada_mostra_mensagem(self):
        resposta = self.client.post(
            reverse("login"), {"username": "demo.operador", "password": "errada"}
        )
        self.assertContains(resposta, "Usuário ou senha incorretos")


class DevolucaoTelaTests(TelasBase):
    def test_fila_lista_devolucao_pendente(self):
        self.entrar()
        resposta = self.client.get(reverse("fila_devolucoes"))
        self.assertContains(resposta, "Botão do rádio (exemplo)")

    def test_peca_danificada_no_estoque_mostra_aviso_e_nao_salva(self):
        self.entrar()
        resposta = self.client.post(
            reverse("conferir_devolucao", args=[self.devolucao.pk]),
            {"condicao": "danificada", "destino": "estoque"},
        )
        self.assertContains(resposta, "Peça danificada não pode voltar ao estoque")
        self.devolucao.refresh_from_db()
        self.assertEqual(self.devolucao.status, Devolucao.Status.PENDENTE)

    def test_conferencia_valida_salva_e_mostra_ajuste_do_bling(self):
        self.entrar()
        resposta = self.client.post(
            reverse("conferir_devolucao", args=[self.devolucao.pk]),
            {"condicao": "danificada", "destino": "descarte", "observacao": "Trincada"},
            follow=True,
        )
        self.assertContains(resposta, "Dar saída por descarte")
        self.devolucao.refresh_from_db()
        self.assertEqual(self.devolucao.status, Devolucao.Status.CONFERIDA)
        self.assertEqual(self.devolucao.conferido_por, self.usuario)

    def test_devolucao_conferida_sai_da_fila(self):
        self.entrar()
        self.devolucao.conferir(self.usuario, "ok", "estoque")
        resposta = self.client.get(reverse("fila_devolucoes"))
        self.assertContains(resposta, "Nenhuma devolução pendente")


class RecebimentoTelaTests(TelasBase):
    def dados(self, recebida):
        return {
            "produto": self.produto.pk, "fornecedor": "Fornecedor Exemplo",
            "quantidade_comprada": 100, "quantidade_recebida": recebida,
            "condicao": "ok",
        }

    def test_100_comprados_98_recebidos_mostra_divergencia_e_ajuste(self):
        self.entrar()
        resposta = self.client.post(reverse("registrar_recebimento"), self.dados(98), follow=True)
        self.assertContains(resposta, "Divergência de 2 unidades")
        self.assertContains(resposta, "Corrigir o saldo de 100 para 98")
        self.assertEqual(Recebimento.objects.get().status, Recebimento.Status.COM_DIVERGENCIA)

    def test_sem_divergencia(self):
        self.entrar()
        resposta = self.client.post(reverse("registrar_recebimento"), self.dados(100), follow=True)
        self.assertContains(resposta, "sem divergência")

    def test_quantidade_negativa_e_recusada(self):
        self.entrar()
        resposta = self.client.post(reverse("registrar_recebimento"), self.dados(-5))
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(Recebimento.objects.count(), 0)
