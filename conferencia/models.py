from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Produto(models.Model):
    """Peça cadastrada pela loja (cadastro manual na primeira versão)."""

    codigo_sku = models.CharField("Código (SKU)", max_length=50, unique=True)
    descricao = models.CharField("Descrição", max_length=200)
    ativo = models.BooleanField("Ativo", default=True)

    class Meta:
        ordering = ["codigo_sku"]

    def __str__(self):
        return f"{self.codigo_sku} - {self.descricao}"


class Recebimento(models.Model):
    """Conferência de uma compra recebida de fornecedor."""

    class Condicao(models.TextChoices):
        OK = "ok", "Ok"
        DANIFICADO = "danificado", "Danificado"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        CONFERIDO = "conferido", "Conferido"
        COM_DIVERGENCIA = "com_divergencia", "Com divergência"

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="recebimentos")
    fornecedor = models.CharField("Fornecedor", max_length=120)
    numero_pedido = models.CharField("Número do pedido", max_length=50, blank=True)
    quantidade_comprada = models.PositiveIntegerField(
        "Quantidade comprada", validators=[MinValueValidator(1)]
    )
    quantidade_recebida = models.PositiveIntegerField("Quantidade recebida", null=True, blank=True)
    condicao = models.CharField("Condição", max_length=12, choices=Condicao.choices, blank=True)
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDENTE)
    observacao = models.TextField("Observação", blank=True)
    conferido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="recebimentos_conferidos",
    )
    data_conferencia = models.DateTimeField("Data da conferência", null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Recebimento {self.pk} - {self.produto.codigo_sku}"

    @property
    def divergencia(self):
        """Comprada menos recebida (None enquanto não conferido)."""
        if self.quantidade_recebida is None:
            return None
        return self.quantidade_comprada - self.quantidade_recebida

    def conferir(self, usuario, quantidade_recebida, condicao, observacao=""):
        """Registra a conferência e define o status e o ajuste a fazer no Bling."""
        if quantidade_recebida is None or quantidade_recebida < 0:
            raise ValidationError("Informe a quantidade recebida, de 0 em diante.")
        if condicao not in self.Condicao.values:
            raise ValidationError("Informe a condição: ok ou danificado.")
        self.quantidade_recebida = quantidade_recebida
        self.condicao = condicao
        self.observacao = observacao
        self.conferido_por = usuario
        self.data_conferencia = timezone.now()
        if quantidade_recebida != self.quantidade_comprada:
            self.status = self.Status.COM_DIVERGENCIA
        else:
            self.status = self.Status.CONFERIDO
        self.save()
        return self

    @property
    def ajuste_bling(self):
        if self.status == self.Status.COM_DIVERGENCIA:
            return (
                f"Corrigir o saldo de {self.quantidade_comprada} "
                f"para {self.quantidade_recebida}"
            )
        return ""


class Devolucao(models.Model):
    """Devolução de cliente que precisa ser conferida antes de voltar ao estoque."""

    class Condicao(models.TextChoices):
        OK = "ok", "Ok"
        DANIFICADA = "danificada", "Danificada"

    class Destino(models.TextChoices):
        ESTOQUE = "estoque", "Estoque"
        REPARO = "reparo", "Reparo"
        DESCARTE = "descarte", "Descarte"

    class Status(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        CONFERIDA = "conferida", "Conferida"

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="devolucoes")
    canal_origem = models.CharField("Canal de origem", max_length=60, blank=True)
    numero_pedido = models.CharField("Número do pedido", max_length=50, blank=True)
    quantidade = models.PositiveIntegerField("Quantidade", validators=[MinValueValidator(1)])
    status = models.CharField("Status", max_length=20, choices=Status.choices, default=Status.PENDENTE)
    condicao = models.CharField("Condição", max_length=12, choices=Condicao.choices, blank=True)
    destino = models.CharField("Destino", max_length=12, choices=Destino.choices, blank=True)
    ajuste_bling = models.CharField("Ajuste a fazer no Bling", max_length=200, blank=True)
    observacao = models.TextField("Observação", blank=True)
    conferido_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.PROTECT, related_name="devolucoes_conferidas",
    )
    data_registro = models.DateTimeField("Data do registro", auto_now_add=True)
    data_conferencia = models.DateTimeField("Data da conferência", null=True, blank=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Devolução {self.pk} - {self.produto.codigo_sku}"

    def conferir(self, usuario, condicao, destino, observacao=""):
        """Conclui a conferência. Regra: peça danificada não pode ir para o estoque."""
        if condicao not in self.Condicao.values:
            raise ValidationError("Informe a condição da peça: ok ou danificada.")
        if destino not in self.Destino.values:
            raise ValidationError("Informe o destino: estoque, reparo ou descarte.")
        if condicao == self.Condicao.DANIFICADA and destino == self.Destino.ESTOQUE:
            raise ValidationError(
                "Peça danificada não pode voltar ao estoque. Escolha Reparo ou Descarte."
            )
        self.condicao = condicao
        self.destino = destino
        self.observacao = observacao
        self.conferido_por = usuario
        self.data_conferencia = timezone.now()
        self.status = self.Status.CONFERIDA
        self.ajuste_bling = {
            self.Destino.ESTOQUE: "Sem ajuste",
            self.Destino.REPARO: "Dar saída por reparo",
            self.Destino.DESCARTE: "Dar saída por descarte",
        }[destino]
        self.save()
        return self
