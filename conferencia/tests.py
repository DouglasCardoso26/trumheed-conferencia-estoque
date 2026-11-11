from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
 
from .models import Devolucao, Produto, Recebimento
 
 
class BaseTestCase(TestCase):
    def setUp(self):
        self.usuario = get_user_model().objects.create_user(
            username="demo.operador", password="senha-de-teste-123"
        )
        self.produto = Produto.objects.create(
            codigo_sku="AP-0012", descricao="Botão do rádio (exemplo)"
        )
 
 
class RecebimentoTests(BaseTestCase):
    def novo(self, comprada=100):
        return Recebimento.objects.create(
            produto=self.produto, fornecedor="Fornecedor Exemplo",
            quantidade_comprada=comprada,
        )
 
    def test_divergencia_de_100_comprados_e_98_recebidos(self):
        r = self.novo().conferir(self.usuario, 98, "ok")
        self.assertEqual(r.divergencia, 2)
        self.assertEqual(r.status, Recebimento.Status.COM_DIVERGENCIA)
        self.assertEqual(r.ajuste_bling, "Corrigir o saldo de 100 para 98")
 
    def test_sem_divergencia_fica_conferido(self):
        r = self.novo().conferir(self.usuario, 100, "ok")
        self.assertEqual(r.status, Recebimento.Status.CONFERIDO)
        self.assertEqual(r.ajuste_bling, "")
 
    def test_grava_responsavel_e_data(self):
        r = self.novo().conferir(self.usuario, 100, "ok")
        self.assertEqual(r.conferido_por, self.usuario)
        self.assertIsNotNone(r.data_conferencia)
 
    def test_recusa_quantidade_negativa(self):
        r = self.novo()
        with self.assertRaises(ValidationError):
            r.conferir(self.usuario, -1, "ok")
        r.refresh_from_db()
        self.assertEqual(r.status, Recebimento.Status.PENDENTE)
 
 
class DevolucaoTests(BaseTestCase):
    def nova(self):
        return Devolucao.objects.create(
            produto=self.produto, canal_origem="Mercado Livre",
            numero_pedido="0000-DEMO", quantidade=1,
        )
 
    def test_nasce_pendente(self):
        self.assertEqual(self.nova().status, Devolucao.Status.PENDENTE)
 
    def test_danificada_nao_pode_ir_para_estoque(self):
        d = self.nova()
        with self.assertRaises(ValidationError):
            d.conferir(self.usuario, "danificada", "estoque")
        d.refresh_from_db()
        self.assertEqual(d.status, Devolucao.Status.PENDENTE)
        self.assertEqual(d.destino, "")
 
    def test_danificada_pode_ir_para_descarte(self):
        d = self.nova().conferir(self.usuario, "danificada", "descarte")
        self.assertEqual(d.status, Devolucao.Status.CONFERIDA)
        self.assertEqual(d.ajuste_bling, "Dar saída por descarte")
 
    def test_ok_pode_voltar_ao_estoque(self):
        d = self.nova().conferir(self.usuario, "ok", "estoque")
        self.assertEqual(d.ajuste_bling, "Sem ajuste")
 
    def test_exige_condicao_e_destino(self):
        d = self.nova()
        with self.assertRaises(ValidationError):
            d.conferir(self.usuario, "", "estoque")
        with self.assertRaises(ValidationError):
            d.conferir(self.usuario, "ok", "")