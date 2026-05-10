from django.contrib.auth.backends import BaseBackend
from .models import Cliente

class ClienteAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
        
        cliente = None
        # Intentar buscar primero por nombre_usuario
        try:
            cliente = Cliente.objects.get(nombre_usuario=username)
        except Cliente.DoesNotExist:
            # Si no existe, intentar por correo electrónico
            try:
                cliente = Cliente.objects.get(correo_electronico=username)
            except Cliente.DoesNotExist:
                return None
        
        # Verificar la contraseña
        if cliente and cliente.check_password(password):
            return cliente
        
        return None

    def get_user(self, user_id):
        try:
            return Cliente.objects.get(pk=user_id)
        except Cliente.DoesNotExist:
            return None
