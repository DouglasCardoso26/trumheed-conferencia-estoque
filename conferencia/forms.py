from django import forms

from .models import Devolucao, Produto, Recebimento

CAMPO = {"class": "form-select form-select-lg"}
TEXTO = {"class": "form-control form-control-lg"}


class RecebimentoForm(forms.Form):
    produto = forms.ModelChoiceField(
        label="Produto",
        queryset=Produto.objects.filter(ativo=True),
        widget=forms.Select(attrs=CAMPO),
        empty_label="Escolha o produto",
    )
    fornecedor = forms.CharField(label="Fornecedor", max_length=120, widget=forms.TextInput(attrs=TEXTO))
    numero_pedido = forms.CharField(
        label="Número do pedido (opcional)", max_length=50, required=False,
        widget=forms.TextInput(attrs=TEXTO),
    )
    quantidade_comprada = forms.IntegerField(
        label="Quantidade comprada", min_value=1, widget=forms.NumberInput(attrs=TEXTO)
    )
    quantidade_recebida = forms.IntegerField(
        label="Quantidade recebida", min_value=0, widget=forms.NumberInput(attrs=TEXTO)
    )
    condicao = forms.ChoiceField(
        label="Condição das peças", choices=Recebimento.Condicao.choices,
        widget=forms.RadioSelect,
    )
    observacao = forms.CharField(
        label="Observação (opcional)", required=False,
        widget=forms.Textarea(attrs={**TEXTO, "rows": 3}),
    )


class ConferenciaDevolucaoForm(forms.Form):
    condicao = forms.ChoiceField(
        label="Condição da peça", choices=Devolucao.Condicao.choices,
        widget=forms.RadioSelect,
    )
    destino = forms.ChoiceField(
        label="Para onde vai a peça?", choices=Devolucao.Destino.choices,
        widget=forms.RadioSelect,
    )
    observacao = forms.CharField(
        label="Observação (opcional)", required=False,
        widget=forms.Textarea(attrs={**TEXTO, "rows": 3}),
    )
