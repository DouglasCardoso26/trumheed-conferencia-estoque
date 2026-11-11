Trumheed Automotive: conferência de estoque

MVP de um sistema web para conferir compras de fornecedores e devoluções de clientes antes de o estoque ser considerado disponível, desenvolvido na disciplina de Projeto de Software, a partir do diagnóstico feito com uma microempresa de autopeças de São Paulo/SP.

Problema

A loja vende em marketplaces e usa um ERP para controlar o estoque. As compras são lançadas sem abrir a caixa, e as devoluções são somadas ao estoque automaticamente, sem verificação da peça. Isso já causou furo de estoque e o risco de vender de novo uma peça danificada.

Escopo do MVP
Registro de recebimento de compras, com aviso de divergência entre a quantidade comprada e a recebida.
Fila de devoluções, com condição (ok ou danificada) e destino (estoque, reparo ou descarte).
Regra: peça danificada não pode ir para o estoque.
Indicação do ajuste a fazer no ERP, na primeira versão de forma manual.
Desejável: histórico de conferências.

Fora do escopo: integração com a API do ERP, conferência na embalagem e funções de ERP (notas, financeiro e precificação).

Tecnologias

Python 3.12, Django 5.2 LTS, Bootstrap 5.3, PostgreSQL (SQLite no desenvolvimento) e psycopg 3.

Como executar

(a completar durante o desenvolvimento)

Status

Em desenvolvimento. Todos os dados usados em testes e demonstrações são fictícios.
