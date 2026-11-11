from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ConferenciaDevolucaoForm, RecebimentoForm
from .models import Devolucao, Recebimento


@login_required
def inicio(request):
    pendentes = Devolucao.objects.filter(status=Devolucao.Status.PENDENTE).count()
    return render(request, "conferencia/inicio.html", {"pendentes": pendentes})


@login_required
def fila_devolucoes(request):
    devolucoes = Devolucao.objects.filter(status=Devolucao.Status.PENDENTE).select_related("produto")
    return render(request, "conferencia/fila.html", {"devolucoes": devolucoes})


@login_required
def conferir_devolucao(request, pk):
    devolucao = get_object_or_404(Devolucao, pk=pk)
    if devolucao.status == Devolucao.Status.CONFERIDA:
        return redirect("resultado_devolucao", pk=devolucao.pk)
    form = ConferenciaDevolucaoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        try:
            devolucao.conferir(
                request.user,
                form.cleaned_data["condicao"],
                form.cleaned_data["destino"],
                form.cleaned_data["observacao"],
            )
        except ValidationError as erro:
            form.add_error(None, erro.messages[0])
        else:
            return redirect("resultado_devolucao", pk=devolucao.pk)
    return render(request, "conferencia/conferir_devolucao.html", {"devolucao": devolucao, "form": form})


@login_required
def resultado_devolucao(request, pk):
    devolucao = get_object_or_404(Devolucao, pk=pk, status=Devolucao.Status.CONFERIDA)
    return render(request, "conferencia/resultado_devolucao.html", {"devolucao": devolucao})


@login_required
def registrar_recebimento(request):
    form = RecebimentoForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        dados = form.cleaned_data
        recebimento = Recebimento.objects.create(
            produto=dados["produto"],
            fornecedor=dados["fornecedor"],
            numero_pedido=dados["numero_pedido"],
            quantidade_comprada=dados["quantidade_comprada"],
        )
        recebimento.conferir(
            request.user, dados["quantidade_recebida"], dados["condicao"], dados["observacao"]
        )
        return redirect("resultado_recebimento", pk=recebimento.pk)
    return render(request, "conferencia/recebimento.html", {"form": form})


@login_required
def resultado_recebimento(request, pk):
    recebimento = get_object_or_404(Recebimento, pk=pk)
    return render(request, "conferencia/resultado_recebimento.html", {"recebimento": recebimento})
