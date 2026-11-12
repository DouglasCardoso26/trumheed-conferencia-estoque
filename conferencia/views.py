from django.contrib import messages
from django.db import connection
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

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


@login_required
def historico(request):
    """Lista as conferências já concluídas (recebimentos e devoluções), da mais recente para a mais antiga."""
    itens = []
    recebimentos = (
        Recebimento.objects.exclude(status=Recebimento.Status.PENDENTE)
        .select_related("produto", "conferido_por")
    )
    for r in recebimentos:
        if r.divergencia:
            resultado = f"Divergência de {r.divergencia} unidade(s)"
        else:
            resultado = "Sem divergência"
        itens.append({
            "tipo": "Recebimento",
            "produto": r.produto,
            "resultado": resultado,
            "ajuste": r.ajuste_bling,
            "responsavel": r.conferido_por,
            "data": r.data_conferencia,
            "url": reverse("resultado_recebimento", args=[r.pk]),
        })
    devolucoes = (
        Devolucao.objects.filter(status=Devolucao.Status.CONFERIDA)
        .select_related("produto", "conferido_por")
    )
    for d in devolucoes:
        itens.append({
            "tipo": "Devolução",
            "produto": d.produto,
            "resultado": f"{d.get_condicao_display()}, destino {d.get_destino_display()}",
            "ajuste": d.ajuste_bling,
            "responsavel": d.conferido_por,
            "data": d.data_conferencia,
            "url": reverse("resultado_devolucao", args=[d.pk]),
        })
    itens.sort(key=lambda item: item["data"], reverse=True)
    return render(request, "conferencia/historico.html", {"itens": itens[:100]})


def saude(request):
    """Verificação de saúde para o monitoramento: responde ok se o sistema e o banco estão no ar."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
    except Exception:
        return JsonResponse({"status": "erro"}, status=503)
    return JsonResponse({"status": "ok"})
