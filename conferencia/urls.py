from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("saude/", views.saude, name="saude"),
    path("entrar/", auth_views.LoginView.as_view(), name="login"),
    path("sair/", auth_views.LogoutView.as_view(), name="logout"),
    path("", views.inicio, name="inicio"),
    path("devolucoes/", views.fila_devolucoes, name="fila_devolucoes"),
    path("devolucoes/<int:pk>/conferir/", views.conferir_devolucao, name="conferir_devolucao"),
    path("devolucoes/<int:pk>/resultado/", views.resultado_devolucao, name="resultado_devolucao"),
    path("historico/", views.historico, name="historico"),
    path("recebimentos/novo/", views.registrar_recebimento, name="registrar_recebimento"),
    path("recebimentos/<int:pk>/resultado/", views.resultado_recebimento, name="resultado_recebimento"),
]
