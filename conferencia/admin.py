from django.contrib import admin
 
from .models import Devolucao, Produto, Recebimento
 
 
@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("codigo_sku", "descricao", "ativo")
    search_fields = ("codigo_sku", "descricao")
 
 
@admin.register(Recebimento)
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ("id", "produto", "fornecedor", "quantidade_comprada", "quantidade_recebida", "status")
    list_filter = ("status",)
 
 
@admin.register(Devolucao)
class DevolucaoAdmin(admin.ModelAdmin):
    list_display = ("id", "produto", "quantidade", "status", "condicao", "destino")
    list_filter = ("status", "condicao", "destino")