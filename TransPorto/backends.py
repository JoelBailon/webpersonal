from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

class ClienteBackend(BaseBackend):
    def authenticate(self, request, username_or_email=None, password=None, **kwargs):
        UserModel = get_user_model()

        if username_or_email is None or password is None:
            return None
        
        try:
            # Verifica si el username_or_email contiene un '@' para determinar si es un correo electrónico
            if '@' in username_or_email:
                user = UserModel.objects.get(correo_electronico=username_or_email)
            else:
                user = UserModel.objects.get(nombre_usuario=username_or_email)
        except UserModel.DoesNotExist:
            return None
        except UserModel.MultipleObjectsReturned:
            # Maneja el caso donde hay múltiples objetos devueltos, si aplica
            return None

        # Verifica la contraseña del usuario
        if user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
