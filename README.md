# Trumheed Automotive: conferência de estoque

MVP de um sistema web para conferir compras de fornecedores e devoluções de clientes antes de o estoque ser considerado disponível, desenvolvido na disciplina de Projeto de Software, a partir do diagnóstico feito com uma microempresa de autopeças de São Paulo/SP.

## Problema

A loja vende em marketplaces e usa um ERP para controlar o estoque. As compras são lançadas sem abrir a caixa, e as devoluções são somadas ao estoque automaticamente, sem verificação da peça. Isso já causou furo de estoque e o risco de vender de novo uma peça danificada.

## Escopo do MVP

- Registro de recebimento de compras, com aviso de divergência entre a quantidade comprada e a recebida.
- Fila de devoluções, com condição (ok ou danificada) e destino (estoque, reparo ou descarte).
- Regra: peça danificada não pode ir para o estoque.
- Indicação do ajuste a fazer no ERP, na primeira versão de forma manual.
- Desejável: histórico de conferências.
- Fora do escopo: integração com API do ERP, conferência na embalagem e funções de ERP (notas, financeiro e precificação).

## Tecnologias

Python 3.12, Django 5.2 LTS, Bootstrap 5.3, PostgreSQL (SQLite no desenvolvimento) e psycopg 3.

## Como executar o projeto

Pré-requisitos: Python 3.12 e Git instalados.

(1) Clonar o repositório e entrar na pasta:

    git clone https://github.com/DouglasCardoso26/trumheed-conferencia-estoque.git
    cd trumheed-conferencia-estoque

(2) Criar e ativar o ambiente virtual (Windows PowerShell):

    py -3.12 -m venv .venv
    .venv\Scripts\Activate.ps1

(3) Instalar as dependências:

    pip install -r requirements.txt

(4) Definir as variáveis de ambiente de desenvolvimento (exemplo no arquivo .env.example):

    $env:DJANGO_DEBUG = "1"

(5) Criar o banco de dados e um usuário de teste:

    python manage.py migrate
    python manage.py createsuperuser

(6) Iniciar o servidor e abrir http://127.0.0.1:8000/ no navegador:

    python manage.py runserver

Para cadastrar produtos e devoluções de teste, use a área administrativa em http://127.0.0.1:8000/admin/.

## Como rodar os testes

    python manage.py test

O pipeline de CI (GitHub Actions, arquivo .github/workflows/ci.yml) roda a verificação do projeto, a checagem de migrações e todos os testes a cada pull request e a cada push na main.

## Regras de negócio cobertas por testes

(1) Divergência de recebimento: quantidade comprada menos quantidade recebida (exemplo real: 100 comprados e 98 recebidos gera divergência de 2 e o ajuste "Corrigir o saldo de 100 para 98").
(2) Devolução com peça danificada não pode voltar ao estoque; só pode ir para reparo ou descarte.
(3) Todas as telas exigem login.

## Segurança e privacidade

Nenhum segredo fica no repositório: a chave secreta e as configurações vêm de variáveis de ambiente (veja .env.example). O sistema não guarda dados pessoais de clientes.

## Status

Em desenvolvimento. Todos os dados usados em testes e demonstrações são fictícios.