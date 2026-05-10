from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import Cliente, Tarjeta, CooperativaTransporte, Rutas, PagoPasaje, RecargaSaldo
from .forms import ClienteCreationForm, ClienteLoginForm, RecargaSaldoForm, PagoForm
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import random
import string
import json
from django.urls import reverse
from django.http import JsonResponse
import datetime
import cv2
import numpy as np
import base64
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import F
from .models import RecargaSaldo, PagoPasaje, Tarjeta
from django.db.models import Q
from itertools import chain
from operator import attrgetter



def index(request):
    return render(request, 'index.html')

def registro(request):
    if request.method == 'POST':
        form = ClienteCreationForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save(commit=False)

            # Procesar foto tomada por cámara (base64)
            foto_camara_data = request.POST.get('foto_rostro_camara')
            if foto_camara_data:
                try:
                    format, imgstr = foto_camara_data.split(';base64,') 
                    ext = format.split('/')[-1]  # normalmente png o jpeg
                    data = ContentFile(base64.b64decode(imgstr), name=f'{cliente.nombre_usuario}_rostro.{ext}')
                    cliente.foto_rostro = data
                except Exception as e:
                    messages.error(request, f'Error al procesar la foto tomada por cámara: {e}')
                    return render(request, 'registro.html', {'form': form})

            # Si el usuario subió foto como archivo, la asigna (opcional)
            elif 'foto_rostro' in request.FILES:
                cliente.foto_rostro = request.FILES['foto_rostro']

            cliente.set_password(form.cleaned_data['contraseña'])
            cliente.save()

            # Crear tarjeta asociada
            numero_tarjeta = generar_numero_tarjeta()
            fecha_emision = timezone.now().date()
            fecha_expiracion = fecha_emision.replace(year=fecha_emision.year + 3)
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

            messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
            return redirect('iniciosecion')  # Cambia por el nombre real de tu URL login

        else:
            messages.error(request, 'Error en el formulario de registro.')
    else:
        form = ClienteCreationForm()

    return render(request, 'registro.html', {'form': form})

def iniciosecion(request):
    if request.method == 'POST':
        form = ClienteLoginForm(request.POST)
        if form.is_valid():
            username_or_email = form.cleaned_data['username_or_email']
            password = form.cleaned_data['password']

            try:
                cliente_obj = Cliente.objects.get(
                    Q(nombre_usuario=username_or_email) | Q(correo_electronico=username_or_email)
                )
                user = authenticate(request, username=cliente_obj.nombre_usuario, password=password)
            except Cliente.DoesNotExist:
                user = None

            if user is not None:
                login(request, user)
                return redirect('/inicio/')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Formulario inválido.')
    else:
        form = ClienteLoginForm()
    return render(request, 'iniciosecion.html', {'form': form})

@login_required
def inicio(request):
    cliente = request.user
    tarjeta = Tarjeta.objects.filter(id_usuario=cliente).first()
    if not tarjeta:
        messages.error(request, 'No se encontró una tarjeta asociada.')
        return redirect('tarjeta')

    # Obtener pagos y recargas
    pagos = PagoPasaje.objects.filter(id_tarjeta=tarjeta).values(
        'monto', 'fecha_pago', 'id_cooperativa__nombre'
    )
    recargas = RecargaSaldo.objects.filter(id_tarjeta=tarjeta).values(
        'monto', 'fecha_y_hora'
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
            'descripcion': "Recarga de saldo",
            'monto': recarga['monto'],
            'fecha': recarga['fecha_y_hora'],
        })

    # Ordenar movimientos por fecha ascendente para calcular saldo acumulado correctamente
    movimientos_asc = sorted(movimientos, key=lambda x: x['fecha'])

    saldo_temp = Decimal('0.00')
    for mov in movimientos_asc:
        if mov['tipo'] == 'recarga':
            saldo_temp += mov['monto']
        else:  # pago
            saldo_temp -= mov['monto']
        mov['saldo_despues'] = saldo_temp

    saldo_actual = saldo_temp

    # Mostrar movimientos en orden descendente (más recientes primero)
    movimientos_desc = list(reversed(movimientos_asc))

    # Orden de botones (mantener si lo usas en tu proyecto)
    orden_por_defecto = ["recargar", "cooperativas", "informacion_personal", "gestionar_tarjeta"]
    orden_botones = getattr(cliente, 'orden_botones_inicio', None)
    if not orden_botones:
        orden_botones = orden_por_defecto

    botones_info = {
        "recargar": {
            "url": "recargar_saldo",
            "img": "https://img.icons8.com/ios-filled/100/000000/wallet--v1.png",
            "texto": "Recargar"
        },
        "cooperativas": {
            "url": "cooperativas",
            "img": "https://img.icons8.com/ios-filled/100/000000/bus.png",
            "texto": "Cooperativas"
        },
        "informacion_personal": {
            "url": "informacion_personal",
            "img": "https://cdn-icons-png.flaticon.com/512/747/747376.png",
            "texto": "Información Personal"
        },
        "gestionar_tarjeta": {
            "url": "habilitar",
            "svg": True,
            "texto": "Gestionar Tarjeta"
        },
    }

    botones_ordenados = []
    for key in orden_botones:
        if key in botones_info:
            botones_ordenados.append({**botones_info[key], "key": key})

    contexto = {
        'saldo': saldo_actual,
        'movimientos': movimientos_desc,
        'botones': botones_ordenados,
    }

    return render(request, 'inicio.html', contexto)


@login_required
def tarjeta(request):
    cliente = request.user
    tarjeta = Tarjeta.objects.filter(id_usuario=cliente).first()
    if request.method == 'POST':
        if tarjeta and tarjeta.estado == "Inactiva":
            tarjeta.estado = "Activo"
            tarjeta.save()
            messages.success(request, 'Tarjeta activada.')
            return redirect('tarjeta')
        elif tarjeta:
            messages.info(request, 'La tarjeta ya está activa.')
        else:
            messages.error(request, 'No se encontró la tarjeta.')

    contexto = {
        'nombre_usuario': cliente.nombre_usuario,
        'numero_tarjeta': tarjeta.numero_tarjeta if tarjeta else None,
        'fecha_expiracion': tarjeta.fecha_expiracion if tarjeta else None,
        'codigo_seguridad': tarjeta.codigo_seguridad if tarjeta else None,
        'fecha_emision': tarjeta.fecha_emision if tarjeta else None
    }
    return render(request, 'tarjeta.html', contexto)

def generar_numero_tarjeta():
    return ''.join(random.choices(string.digits, k=16))

def generar_codigo_seguridad():
    return ''.join(random.choices(string.digits, k=3))

@login_required
def habilitar(request):
    if request.method == 'POST':
        tarjeta_existente = Tarjeta.objects.filter(id_usuario=request.user).first()
        if tarjeta_existente:
            if tarjeta_existente.estado == "Inactiva":
                tarjeta_existente.estado = "Activo"
                tarjeta_existente.save()
                messages.success(request, 'Tarjeta activada.')
                return redirect('tarjeta')
            else:
                messages.info(request, 'La tarjeta ya está activa.')
        else:
            messages.error(request, 'No se encontró la tarjeta.')
    return render(request, 'habilitar.html')

def cooperativas(request):
    cooperativas = CooperativaTransporte.objects.all()
    return render(request, 'cooperativas.html', {'cooperativas': cooperativas})

def rutas(request, id_cooperativa):
    cooperativa = get_object_or_404(CooperativaTransporte, id_cooperativa=id_cooperativa)
    rutas = Rutas.objects.filter(id_cooperativa=cooperativa)
    return render(request, 'rutas.html', {'cooperativa': cooperativa, 'rutas': rutas})

from decimal import Decimal
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def saldo_view(request):
    usuario = request.user

    tarjeta = Tarjeta.objects.filter(id_usuario=usuario).first()
    if not tarjeta:
        saldo_actual = Decimal('0.00')
        movimientos = []
    else:
        # Obtener pagos y recargas
        pagos = PagoPasaje.objects.filter(id_tarjeta=tarjeta).select_related('id_cooperativa').values(
            'fecha_pago', 'monto', 'id_cooperativa__nombre', 'cantidad_pasajes'
        )
        recargas = RecargaSaldo.objects.filter(id_tarjeta=tarjeta).values(
            'fecha_y_hora', 'monto'
        )

        movimientos_list = []

        for pago in pagos:
            coop_nombre = pago.get('id_cooperativa__nombre', 'Cooperativa desconocida')
            cantidad = pago.get('cantidad_pasajes', 1)
            movimientos_list.append({
                'fecha': pago['fecha_pago'],
                'descripcion': coop_nombre,
                'monto': pago['monto'],
                'tipo': 'pago',
                'cantidad_pasajes': cantidad,
            })

        for recarga in recargas:
            movimientos_list.append({
                'fecha': recarga['fecha_y_hora'],
                'descripcion': 'Recarga realizada',
                'monto': recarga['monto'],
                'tipo': 'recarga',
                'cantidad_pasajes': None,
            })

        # Ordenamos ascendente por fecha para calcular saldo acumulado
        movimientos_list_asc = sorted(movimientos_list, key=lambda x: x['fecha'])
        saldo_temp = Decimal('0.00')

        for mov in movimientos_list_asc:
            if mov['tipo'] == 'recarga':
                saldo_temp += mov['monto']
            else:  # pago
                saldo_temp -= mov['monto']
            mov['saldo_despues'] = saldo_temp

        # Saldo actual calculado
        saldo_actual = saldo_temp

        # Mostrar movimientos descendente (más recientes primero)
        movimientos = list(reversed(movimientos_list_asc))

    context = {
        'saldo': saldo_actual,
        'movimientos': movimientos,
    }
    return render(request, 'saldo.html', context)


@login_required
def recargar_saldo(request):
    cliente = request.user
    tarjeta = Tarjeta.objects.filter(id_usuario=cliente).first()
    if not tarjeta:
        messages.error(request, 'No se encontró la tarjeta.')
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
            messages.success(request, 'Saldo recargado exitosamente.')
            return redirect('saldo')
        else:
            messages.error(request, 'Formulario inválido.')
    else:
        form = RecargaSaldoForm()

    return render(request, 'recargar_saldo.html', {'form': form})


@login_required
def realizar_pago(request):
    if request.method == "POST" and request.headers.get('Content-Type') == 'application/json':
        # POST JSON (desde QR)
        try:
            data = json.loads(request.body)
            codigo_qr = data.get('codigo_qr')
            cooperativa_id = data.get('id_cooperativa')

            # Recuperar cantidad_pasajes desde sesión (NO desde JSON)
            cantidad_pasajes = request.session.get('cantidad_pasajes', 1)
            try:
                cantidad_pasajes = int(cantidad_pasajes)
                if cantidad_pasajes < 1:
                    cantidad_pasajes = 1
            except Exception:
                cantidad_pasajes = 1

            cooperativa_id_sesion = request.session.get('cooperativa_id')

            if str(cooperativa_id) != str(cooperativa_id_sesion):
                return JsonResponse({"success": False, "error": "Datos inconsistentes."})

            precio_unitario = Decimal("0.40")
            total = precio_unitario * cantidad_pasajes

            tarjeta = Tarjeta.objects.filter(id_usuario=request.user).first()
            if not tarjeta:
                return JsonResponse({"success": False, "error": "No se encontró tarjeta asociada."})

            if tarjeta.saldo_asociado < total:
                return JsonResponse({"success": False, "error": "Saldo insuficiente."})

            cooperativa = get_object_or_404(CooperativaTransporte, id_cooperativa=cooperativa_id)

            tarjeta.saldo_asociado -= total
            tarjeta.save()

            PagoPasaje.objects.create(
                id_tarjeta=tarjeta,
                monto=total,
                id_cooperativa=cooperativa,
                cantidad_pasajes=cantidad_pasajes,
            )

            # Limpiar sesión
            request.session.pop('cantidad_pasajes', None)
            request.session.pop('cooperativa_id', None)

            return JsonResponse({"success": True, "message": "Pago realizado con éxito", "redirect_url": reverse('saldo')})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    elif request.method == "POST":
        # POST normal (formulario)
        try:
            cooperativa_id = request.POST.get("cooperativa")
            cantidad_pasajes = request.POST.get("cantidad_pasajes", 1)
            try:
                cantidad_pasajes = int(cantidad_pasajes)
                if cantidad_pasajes < 1:
                    cantidad_pasajes = 1
            except Exception:
                cantidad_pasajes = 1

            cooperativa = get_object_or_404(CooperativaTransporte, id_cooperativa=cooperativa_id)

            # Guardar en sesión para usar luego en el pago QR
            request.session['cantidad_pasajes'] = cantidad_pasajes
            request.session['cooperativa_id'] = cooperativa_id

            return render(request, "pago_por_qr.html", {
                "cooperativa": cooperativa,
                "cantidad_pasajes": cantidad_pasajes,
                "precio_unitario": Decimal("0.40"),
                "total": cantidad_pasajes * Decimal("0.40"),
            })
        except Exception as e:
            from django.contrib import messages
            messages.error(request, f"Error al procesar datos: {str(e)}")
            from .forms import PagoForm
            form = PagoForm()
            return render(request, "realizar_pago.html", {"form": form})

    else:
        from .forms import PagoForm
        form = PagoForm()
        return render(request, "realizar_pago.html", {"form": form})

@login_required
def pago_por_qr(request, id_cooperativa):
    cooperativa = get_object_or_404(CooperativaTransporte, id_cooperativa=id_cooperativa)
    cantidad_pasajes = request.session.get('cantidad_pasajes', 1)  # default 1 si no está
    return render(request, 'pago_por_qr.html', {
        'cooperativa': cooperativa,
        'cantidad_pasajes': cantidad_pasajes,
    })


@csrf_exempt
def procesar_pago_qr(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)

            cantidad_pasajes = int(data.get('cantidad_pasajes', 1))
            print("Cantidad pasajes recibida:", cantidad_pasajes)

            id_cooperativa = data.get('id_cooperativa')

            cliente = request.user
            tarjeta = Tarjeta.objects.get(id_usuario=cliente)
            cooperativa = CooperativaTransporte.objects.get(pk=id_cooperativa)

            precio_unitario = Decimal('0.40')
            monto_total = precio_unitario * cantidad_pasajes

            if tarjeta.saldo_asociado < monto_total:
                return JsonResponse({'success': False, 'error': 'Saldo insuficiente'})

            tarjeta.saldo_asociado -= monto_total
            tarjeta.save()

            PagoPasaje.objects.create(
                id_tarjeta=tarjeta,
                monto=monto_total,
                id_cooperativa=cooperativa,
                cantidad_pasajes=cantidad_pasajes,
                fecha_pago=timezone.now()
            )

            return JsonResponse({
                'success': True,
                'redirect_url': reverse('saldo')
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)



@login_required
def informacion_personal(request):
    return render(request, 'informacion_personal.html', {'user': request.user})

def recuperar_contrasena(request):
    if request.method == 'POST':
        entrada = request.POST.get('usuario_recuperacion')
        nueva_contrasena = request.POST.get('nueva_contrasena')
        confirmar_contrasena = request.POST.get('confirmar_contrasena')

        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('iniciosecion')

        try:
            cliente = Cliente.objects.get(
                correo_electronico=entrada
            ) if '@' in entrada else Cliente.objects.get(nombre_usuario=entrada)

            cliente.set_password(nueva_contrasena)
            cliente.save()

            messages.success(request, 'Contraseña actualizada correctamente.')
            return redirect('iniciosecion')

        except Cliente.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('iniciosecion')
    else:
        return redirect('iniciosecion')
    
def escaneo_qr(request, id_cooperativa):
    return render(request, 'escaneo_qr.html', {'id_cooperativa': id_cooperativa})


@csrf_exempt  # Mejor usar csrf token, aquí solo ejemplo rápido
def actualizar_tema(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        tema = data.get('tema', 'light')
        if tema in ['light', 'dark']:
            request.user.tema_preferido = tema
            request.user.save()
            return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

def vista_inicio(request):
    tema = 'light'
    if request.user.is_authenticated:
        tema = request.user.tema_preferido
    return render(request, 'inicio.html', {'tema_usuario': tema})


@login_required
def editar_orden_botones(request):
    user = request.user
    if request.method == 'POST':
        orden = json.loads(request.body.decode('utf-8')).get('orden', [])
        user.orden_botones_inicio = orden
        user.save()
        return JsonResponse({'success': True})

    orden_actual = user.orden_botones_inicio or ["recargar", "cooperativas", "informacion_personal", "gestionar_tarjeta"]

    # Preparar texto legible para plantilla
    orden_legible = []
    for boton in orden_actual:
        texto = boton.replace("_", " ").title()
        orden_legible.append({'key': boton, 'texto': texto})

    return render(request, 'editar_orden_botones.html', {'orden': orden_legible})


def editar_usuario(request):
    if request.method == 'POST':
        user = request.user
        user.nombre_usuario = request.POST.get('nombre_usuario')
        user.correo_electronico = request.POST.get('correo_electronico')
        user.numero_telefonico = request.POST.get('numero_telefonico')
        user.save()
        messages.success(request, 'Información actualizada correctamente.')
        return redirect('informacion_personal')  # Cambia si tu vista tiene otro nombre
    



# Cargar clasificador Haar Cascade para detección facial
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@csrf_exempt
def reconocimiento_facial(request):
    if request.method == 'POST':
        try:
            data = request.POST.get('image')
            if not data:
                return JsonResponse({'success': False, 'error': 'No se recibió imagen'})

            header, encoded = data.split(',', 1)
            img_bytes = base64.b64decode(encoded)
            np_arr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

            if len(faces) == 0:
                return JsonResponse({'success': False, 'error': 'No se detectó ningún rostro.'})

            return JsonResponse({'success': True, 'faces_detected': len(faces)})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)



# Inicializa el reconocedor LBPH 
recognizer = cv2.face.LBPHFaceRecognizer_create()

def preparar_imagen_gray(imagen_path):
    img = cv2.imread(imagen_path)
    if img is None:
        return None
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return gray

@csrf_exempt
def login_facial(request):
    if request.method == 'POST':
        try:
            foto_subida = request.FILES.get('foto_rostro')
            if not foto_subida:
                return JsonResponse({'success': False, 'error': 'No se recibió la imagen.'})

            # Convertir a imagen OpenCV
            imagen_bytes = foto_subida.read()
            nparr = np.frombuffer(imagen_bytes, np.uint8)
            imagen_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if imagen_cv is None:
                return JsonResponse({'success': False, 'error': 'Imagen inválida.'})

            # Detección de rostro
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gris = cv2.cvtColor(imagen_cv, cv2.COLOR_BGR2GRAY)
            rostros = face_cascade.detectMultiScale(gris, scaleFactor=1.2, minNeighbors=5)

            if len(rostros) == 0:
                return JsonResponse({'success': False, 'error': 'No se detectó ningún rostro en la imagen.'})

            # Usar el primer rostro detectado
            (x, y, w, h) = rostros[0]
            gris_rostro = gris[y:y+h, x:x+w]
            gris_rostro = cv2.resize(gris_rostro, (200, 200))

            # Obtener clientes
            clientes = Cliente.objects.exclude(foto_rostro='').exclude(foto_rostro__isnull=True)
            if not clientes.exists():
                return JsonResponse({'success': False, 'error': 'No hay rostros registrados para comparar.'})

            caras = []
            etiquetas = []
            label_id_map = {}

            for idx, cliente in enumerate(clientes):
                try:
                    rostro_path = cliente.foto_rostro.path
                    gray_reg = preparar_imagen_gray(rostro_path)
                    if gray_reg is None:
                        continue

                    # Detectar rostro en la imagen registrada
                    rostros_reg = face_cascade.detectMultiScale(gray_reg, scaleFactor=1.2, minNeighbors=5)
                    if len(rostros_reg) == 0:
                        continue
                    (x_r, y_r, w_r, h_r) = rostros_reg[0]
                    gray_reg = gray_reg[y_r:y_r+h_r, x_r:x_r+w_r]
                    gray_reg = cv2.resize(gray_reg, (200, 200))

                    caras.append(gray_reg)
                    etiquetas.append(idx)
                    label_id_map[idx] = cliente
                except Exception:
                    continue

            if len(caras) == 0:
                return JsonResponse({'success': False, 'error': 'No se pudo procesar ninguna coincidencia.'})

            
            recognizer = cv2.face.LBPHFaceRecognizer_create()
            recognizer.train(caras, np.array(etiquetas))

            label_pred, conf = recognizer.predict(gris_rostro)

            # Parámetros
            UMBRAL_CONFIANZA = 50

            if conf < UMBRAL_CONFIANZA:
                backend = settings.AUTHENTICATION_BACKENDS[0]
                login(request, label_id_map[label_pred], backend=backend)
                return JsonResponse({'success': True, 'redirect_url': '/inicio/'})
            else:
                return JsonResponse({'success': False, 'error': 'No se encontró coincidencia facial segura.'})

        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Error interno: {str(e)}'})

    return render(request, 'iniciosecion.html')