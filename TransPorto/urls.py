from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import recargar_saldo, realizar_pago
from django.contrib.auth import views as auth_views
from .views import login_facial

urlpatterns = [
    path('inicio/', views.inicio, name='inicio'),
    path('iniciosecion/', views.iniciosecion, name='iniciosecion'),
    path('registro/', views.registro, name='registro'),
    path('saldo/', views.saldo_view, name='saldo'),
    path('tarjeta/', views.tarjeta, name='tarjeta'),
    path('cooperativa/', views.cooperativas, name='cooperativas'),
    path('rutas/<int:id_cooperativa>/', views.rutas, name='rutas'),
    path('habilitar/', views.habilitar, name='habilitar'),
    path('recargar-saldo/', recargar_saldo, name='recargar_saldo'),
    path('logout/', auth_views.LogoutView.as_view(next_page='iniciosecion'), name='logout'),
    path('informacion/', views.informacion_personal, name='informacion_personal'),
    path('recuperar-contrasena/', views.recuperar_contrasena, name='recuperar_contrasena'),
    path('realizar_pago/', realizar_pago, name='realizar_pago'),
    path('escaneo-qr/<int:id_cooperativa>/', views.escaneo_qr, name='escaneo_qr'),
    path('procesar_pago_qr/', views.procesar_pago_qr, name='procesar_pago_qr'),
    path('pago_por_qr/<int:id_cooperativa>/', views.pago_por_qr, name='pago_por_qr'),
    path('actualizar-tema/', views.actualizar_tema, name='actualizar_tema'),
    path('editar-orden-botones/', views.editar_orden_botones, name='editar_orden_botones'),
    path('editar-usuario/', views.editar_usuario, name='editar_usuario'),
    path('login-facial/', views.login_facial, name='login_facial'),
    path('login_facial/', login_facial, name='login_facial'),
    path('inicio/', views.inicio, name='inicio'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
