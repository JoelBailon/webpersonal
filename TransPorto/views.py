from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Q, F
from django.urls import reverse
from django.conf import settings
from django.core.files.base import ContentFile

from django.http import HttpResponse

def prueba(request):
    return HttpResponse("FUNCIONANDO VERCEL")

from .models import (
    Cliente,
    Tarjeta,
    CooperativaTransporte,
    Rutas,
    PagoPasaje,
    RecargaSaldo
)

from .forms import (
    ClienteCreationForm,
    ClienteLoginForm,
    RecargaSaldoForm,
    PagoForm
)

from decimal import Decimal
from itertools import chain
from operator import attrgetter

import random
import string
import json
import datetime
import base64

# OpenCV compatible con Vercel
import cv2
import numpy as np


def index(request):
    return render(request, 'index.html')


def registro(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST, request.FILES)

        if form.is_valid():
            cliente = form.save(commit=False)

            foto_camara_data = request.POST.get('foto_rostro_camara')

            if foto_camara_data:
                try:
                    format, imgstr = foto_camara_data.split(';base64,')
                    ext = format.split('/')[-1]

                    data = ContentFile(
                        base64.b64decode(imgstr),
                        name=f'{cliente.nombre_usuario}_rostro.{ext}'
                    )

                    cliente.foto_rostro = data

                except Exception as e:
                    messages.error(
                        request,
                        f'Error al procesar la foto: {e}'
                    )

                    return render(
                        request,
                        'registro.html',
                        {'form': form}
                    )

            elif 'foto_rostro' in request.FILES:
                cliente.foto_rostro = request.FILES['foto_rostro']

            cliente.set_password(form.cleaned_data['contraseña'])
            cliente.save()

            numero_tarjeta = generar_numero_tarjeta()

            fecha_emision = timezone.now().date()

            fecha_expiracion = fecha_emision.replace(
                year=fecha_emision.year + 3
            )

            codigo_seguridad = generar_codigo_seguridad()

            Tarjeta.objects.create(
                id_usuario=cliente,
                numero_tarjeta=numero_tarjeta,
                fecha_emision=fecha_emision,
                fecha_expiracion=fecha_expiracion,
                estado="Inactiva",
                saldo_asociado=Decimal('0.00'),
                codigo_seguridad=codigo_seguridad
            )

            messages.success(
                request,
                'Registro exitoso.'
            )

            return redirect('iniciosecion')

        else:
            messages.error(
                request,
                'Error en el formulario.'
            )

    else:
        form = ClienteCreationForm()

    return render(
        request,
        'registro.html',
        {'form': form}
    )


def iniciosecion(request):

    if request.method == 'POST':

        form = ClienteLoginForm(request.POST)

        if form.is_valid():

            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            try:
                cliente_obj = Cliente.objects.get(
                    Q(nombre_usuario=username_or_email) |
                    Q(correo_electronico=username_or_email)
                )

                user = authenticate(
                    request,
                    username=cliente_obj.nombre_usuario,
                    password=password
                )

            except Cliente.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                return redirect('/inicio/')

            else:
                messages.error(
                    request,
                    'Credenciales incorrectas.'
                )

        else:
            messages.error(
                request,
                'Formulario inválido.'
            )

    else:
        form = ClienteLoginForm()

    return render(
        request,
        'iniciosecion.html',
        {'form': form}
    )


@login_required
def inicio(request):

    cliente = request.user

    tarjeta = Tarjeta.objects.filter(
        id_usuario=cliente
    ).first()

    if not tarjeta:
        messages.error(
            request,
            'No se encontró tarjeta.'
        )

        return redirect('tarjeta')

    pagos = PagoPasaje.objects.filter(
        id_tarjeta=tarjeta
    ).values(
        'monto',
        'fecha_pago',
        'id_cooperativa__nombre'
    )

    recargas = RecargaSaldo.objects.filter(
        id_tarjeta=tarjeta
    ).values(
        'monto',
        'fecha_y_hora'
    )

    movimientos = []

    for pago in pagos:

        movimientos.append({
            'tipo': 'pago',
            'descripcion': f"Pago - {pago['id_cooperativa__nombre'] or 'Desconocida'}",
            'monto': pago['monto'],
            'fecha': pago['fecha_pago'],
        })

    for recarga in recargas:

        movimientos.append({
            'tipo': 'recarga',
            'descripcion': 'Recarga',
            'monto': recarga['monto'],
            'fecha': recarga['fecha_y_hora'],
        })

    movimientos_asc = sorted(
        movimientos,
        key=lambda x: x['fecha']
    )

    saldo_temp = Decimal('0.00')

    for mov in movimientos_asc:

        if mov['tipo'] == 'recarga':
            saldo_temp += mov['monto']

        else:
            saldo_temp -= mov['monto']

        mov['saldo_despues'] = saldo_temp

    saldo_actual = saldo_temp

    movimientos_desc = list(
        reversed(movimientos_asc)
    )

    contexto = {
        'saldo': saldo_actual,
        'movimientos': movimientos_desc,
    }

    return render(
        request,
        'inicio.html',
        contexto
    )


@login_required
def tarjeta(request):

    cliente = request.user

    tarjeta = Tarjeta.objects.filter(
        id_usuario=cliente
    ).first()

    if request.method == 'POST':

        if tarjeta and tarjeta.estado == "Inactiva":

            tarjeta.estado = "Activo"
            tarjeta.save()

            messages.success(
                request,
                'Tarjeta activada.'
            )

            return redirect('tarjeta')

    contexto = {
        'nombre_usuario': cliente.nombre_usuario,
        'numero_tarjeta': tarjeta.numero_tarjeta if tarjeta else None,
        'fecha_expiracion': tarjeta.fecha_expiracion if tarjeta else None,
        'codigo_seguridad': tarjeta.codigo_seguridad if tarjeta else None,
        'fecha_emision': tarjeta.fecha_emision if tarjeta else None
    }

    return render(
        request,
        'tarjeta.html',
        contexto
    )


def generar_numero_tarjeta():
    return ''.join(
        random.choices(string.digits, k=16)
    )


def generar_codigo_seguridad():
    return ''.join(
        random.choices(string.digits, k=3)
    )


@login_required
def habilitar(request):

    tarjeta_existente = Tarjeta.objects.filter(
        id_usuario=request.user
    ).first()

    if request.method == 'POST':

        if tarjeta_existente:

            if tarjeta_existente.estado == "Inactiva":

                tarjeta_existente.estado = "Activo"
                tarjeta_existente.save()

                messages.success(
                    request,
                    'Tarjeta activada.'
                )

                return redirect('tarjeta')

    return render(request, 'habilitar.html')


def cooperativas(request):

    cooperativas = CooperativaTransporte.objects.all()

    return render(
        request,
        'cooperativas.html',
        {'cooperativas': cooperativas}
    )


def rutas(request, id_cooperativa):

    cooperativa = get_object_or_404(
        CooperativaTransporte,
        id_cooperativa=id_cooperativa
    )

    rutas = Rutas.objects.filter(
        id_cooperativa=cooperativa
    )

    return render(
        request,
        'rutas.html',
        {
            'cooperativa': cooperativa,
            'rutas': rutas
        }
    )


@login_required
def saldo_view(request):

    usuario = request.user

    tarjeta = Tarjeta.objects.filter(
        id_usuario=usuario
    ).first()

    saldo_actual = Decimal('0.00')
    movimientos = []

    if tarjeta:

        pagos = PagoPasaje.objects.filter(
            id_tarjeta=tarjeta
        )

        recargas = RecargaSaldo.objects.filter(
            id_tarjeta=tarjeta
        )

        for pago in pagos:
            saldo_actual -= pago.monto

        for recarga in recargas:
            saldo_actual += recarga.monto

    context = {
        'saldo': saldo_actual,
        'movimientos': movimientos,
    }

    return render(
        request,
        'saldo.html',
        context
    )


@login_required
def recargar_saldo(request):

    cliente = request.user

    tarjeta = Tarjeta.objects.filter(
        id_usuario=cliente
    ).first()

    if not tarjeta:

        messages.error(
            request,
            'No se encontró tarjeta.'
        )

        return redirect('tarjeta')

    if request.method == 'POST':

        form = RecargaSaldoForm(request.POST)

        if form.is_valid():

            monto = form.cleaned_data['monto']

            tarjeta.saldo_asociado += monto
            tarjeta.save()

            RecargaSaldo.objects.create(
                id_tarjeta=tarjeta,
                monto=monto
            )

            messages.success(
                request,
                'Saldo recargado.'
            )

            return redirect('saldo')

    else:
        form = RecargaSaldoForm()

    return render(
        request,
        'recargar_saldo.html',
        {'form': form}
    )


@login_required
def informacion_personal(request):

    return render(
        request,
        'informacion_personal.html',
        {'user': request.user}
    )


def recuperar_contrasena(request):

    if request.method == 'POST':

        entrada = request.POST.get(
            'usuario_recuperacion'
        )

        nueva_contrasena = request.POST.get(
            'nueva_contrasena'
        )

        confirmar_contrasena = request.POST.get(
            'confirmar_contrasena'
        )

        if nueva_contrasena != confirmar_contrasena:

            messages.error(
                request,
                'Las contraseñas no coinciden.'
            )

            return redirect('iniciosecion')

        try:

            cliente = Cliente.objects.get(
                correo_electronico=entrada
            ) if '@' in entrada else Cliente.objects.get(
                nombre_usuario=entrada
            )

            cliente.set_password(nueva_contrasena)
            cliente.save()

            messages.success(
                request,
                'Contraseña actualizada.'
            )

            return redirect('iniciosecion')

        except Cliente.DoesNotExist:

            messages.error(
                request,
                'Usuario no encontrado.'
            )

            return redirect('iniciosecion')

    return redirect('iniciosecion')


# =========================
# FUNCIONES DESACTIVADAS
# PARA COMPATIBILIDAD VERCEL
# =========================

@csrf_exempt
def reconocimiento_facial(request):

    return JsonResponse({
        'success': False,
        'error': 'Reconocimiento facial desactivado en Vercel.'
    })


@csrf_exempt
def login_facial(request):

    return JsonResponse({
        'success': False,
        'error': 'Login facial desactivado en Vercel.'
    })
