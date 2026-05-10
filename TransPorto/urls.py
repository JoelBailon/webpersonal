from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    # Página principal
    path('', views.index, name='index'),

    # Autenticación
    path('iniciosecion/', views.iniciosecion, name='iniciosecion'),
    path('registro/', views.registro, name='registro'),
    path('logout/', auth_views.LogoutView.as_view(next_page='iniciosecion'), name='logout'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),

    # Inicio usuario
    path('inicio/', views.inicio, name='inicio'),

    # Tarjeta
    path('tarjeta/', views.tarjeta, name='tarjeta'),
    path('habilitar/', views.habilitar, name='habilitar'),

    # Saldo y recargas
    path('saldo/', views.saldo_view, name='saldo'),
    path('recargar-saldo/', views.recargar_saldo, name='recargar_saldo'),

    # Cooperativas y rutas
    path('cooperativas/', views.cooperativas, name='cooperativas'),
    path('rutas/<int:id_cooperativa>/', views.rutas, name='rutas'),

    # Pagos QR
    path('realizar_pago/', views.realizar_pago, name='realizar_pago'),
    path('escaneo-qr/<int:id_cooperativa>/', views.escaneo_qr, name='escaneo_qr'),
    path('procesar_pago_qr/', views.procesar_pago_qr, name='procesar_pago_qr'),
    path('pago_por_qr/<int:id_cooperativa>/', views.pago_por_qr, name='pago_por_qr'),

    # Usuario
    path('informacion/', views.informacion_personal, name='informacion_personal'),
    path('editar-usuario/', views.editar_usuario, name='editar_usuario'),

    # Personalización
    path('actualizar-tema/', views.actualizar_tema, name='actualizar_tema'),
    path('editar-orden-botones/', views.editar_orden_botones, name='editar_orden_botones'),

    # Reconocimiento facial
    path('reconocimiento_facial/', views.reconocimiento_facial, name='reconocimiento_facial'),
    path('login-facial/', views.login_facial, name='login_facial'),
]

# Archivos multimedia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
