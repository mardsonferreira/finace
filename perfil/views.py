from django.db.models import Sum, DecimalField

from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.messages import constants

from .models import Conta, Categoria
from extrato.models import Valores

from .utils import calcula_total

def home(request):
    contas = Conta.objects.all()
    saldo_total = calcula_total(contas, 'valor')
    return render(request, 'home.html', {'contas': contas, 'saldo_total': saldo_total,})


def gerenciar(request):
    contas = Conta.objects.all()
    categorias = Categoria.objects.all()

    total = calcula_total(contas, 'valor')

    bancos = [ {'code': code, 'name': name} for code, name in Conta.banco_choices ]

    return render(
        request,
        'gerenciar.html', 
        {
            'contas': contas,
            'total_contas': total,
            'categorias': categorias,
            'bancos': bancos
        }
    )

def cadastrar_banco(request):
    apelido = request.POST.get('apelido')
    banco = request.POST.get('banco')
    tipo = request.POST.get('tipo')
    valor = request.POST.get('valor')
    icone = request.FILES.get('icone')
    
    if len(apelido.strip()) == 0 or len(valor.strip()) == 0:
        messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
        return redirect('/perfil/gerenciar/')
    
    conta = Conta(
        apelido = apelido,
        banco=banco,
        tipo=tipo,
        valor=valor,
        icone=icone
    )

    conta.save()

    messages.add_message(request, constants.SUCCESS, 'Conta cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def deletar_banco(request, id):
    conta = Conta.objects.get(id=id)
    conta.delete()
    
    messages.add_message(request, constants.SUCCESS, 'Conta removida com sucesso')
    return redirect('/perfil/gerenciar/')

def cadastrar_categoria(request):
    nome = request.POST.get('categoria')
    essencial = bool(request.POST.get('essencial'))

    categoria = Categoria(
        categoria=nome,
        essencial=essencial
    )

    categoria.save()

    messages.add_message(request, constants.SUCCESS, 'Categoria cadastrada com sucesso')
    return redirect('/perfil/gerenciar/')

def update_categoria(request, id):
    categoria = Categoria.objects.get(id=id)

    categoria.essencial = not categoria.essencial

    categoria.save()

    return redirect('/perfil/gerenciar/')

def dashboard(request):
    dados = {}

    valores_queryset = valores_queryset = Categoria.objects \
        .all() \
        .annotate(total=Sum("valores__valor", distinct=True, output_field=DecimalField())) \
        .values("categoria", "total") \

    for valores in valores_queryset:
        dados[valores["categoria"]] = float(valores["total"]) if  valores["total"] is not None else 0

    return render(request, 'dashboard.html', {'labels': list(dados.keys()), 'values': list(dados.values())})